from mlflow.deployments import get_deploy_client
from databricks.sdk import WorkspaceClient
import json
import uuid

def _throw_unexpected_endpoint_format():
    raise Exception("This app can only run against:"
                    "1) Databricks foundation model or external model endpoints with the chat task type (described in https://docs.databricks.com/aws/en/machine-learning/model-serving/score-foundation-models#chat-completion-model-query)\n"
                    "2) Databricks agent serving endpoints that implement the conversational agent schema documented "
                    "in https://docs.databricks.com/aws/en/generative-ai/agent-framework/author-agent")


def query_endpoint_stream(endpoint_name: str, messages: list[dict[str, str]], max_tokens: int, return_traces: bool):
    """Streams chat-completions style chunks and converts to ChatAgent-style streaming deltas."""
    client = get_deploy_client("databricks")

    # Extract the user message from the messages array
    user_message = ""
    for msg in messages:
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    # Prepare input payload for multi-agent supervisor
    inputs = {
        "input": [{"role": "user", "content": user_message}],
        "max_output_tokens": max_tokens,
    }
    if return_traces:
        inputs["databricks_options"] = {"return_trace": True}

    stream_id = str(uuid.uuid4())  # Generate unique ID for the stream

    try:
        for chunk in client.predict_stream(endpoint=endpoint_name, inputs=inputs):
            if "choices" in chunk:
                choices = chunk["choices"]
                if len(choices) > 0:
                    # Convert from chat completions to ChatAgent format
                    content = choices[0]["delta"].get("content", "")
                    if content:
                        yield {
                            "delta": {
                                "role": "assistant",
                                "content": content,
                                "id": stream_id
                            },
                        }
            elif "delta" in chunk:
                # Yield the ChatAgentChunk directly
                yield chunk
            else:
                _throw_unexpected_endpoint_format()
    except Exception as e:
        # Fallback to non-streaming if streaming fails
        print(f"Streaming failed, falling back to non-streaming: {e}")
        response_messages, request_id = query_endpoint(endpoint_name, messages, max_tokens, return_traces)
        if response_messages and len(response_messages) > 0:
            content = response_messages[0].get("content", "")
            if content:
                yield {
                    "delta": {
                        "role": "assistant",
                        "content": content,
                        "id": stream_id
                    },
                }


def query_endpoint(endpoint_name, messages, max_tokens, return_traces):
    """
    Query an endpoint, returning the string message content and request ID for feedback.
    This function handles both foundation model endpoints and multi-agent supervisor endpoints.
    """
    client = get_deploy_client("databricks")
    
    # Extract the user message from the messages array
    user_message = ""
    for msg in messages:
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    # Prepare input payload - try different formats based on endpoint type
    inputs = {
        "input": [{"role": "user", "content": user_message}],
        "max_output_tokens": max_tokens,
    }
    
    if return_traces:
        inputs["databricks_options"] = {"return_trace": True}
    
    try:
        res = client.predict(endpoint=endpoint_name, inputs=inputs)
    except Exception as e:
        print(f"Error calling endpoint: {e}")
        return [{"role": "assistant", "content": "I encountered an issue while processing your request. Please try again in a moment."}], None
    
    # Extract request_id
    request_id = res.get("databricks_output", {}).get("databricks_request_id") if res else None
    
    # Handle different response formats
    if "input" in res and isinstance(res["input"], list):
        # Multi-agent supervisor returns conversation history in 'input' field
        conversation_history = res["input"]
        final_response = extract_final_assistant_response(conversation_history)
        if final_response:
            return [{"role": "assistant", "content": final_response}], request_id
    
    # Handle output field responses
    if "output" in res:
        output_content = res["output"]
        
        if isinstance(output_content, str):
            # Direct string output
            if "Handed off to:" in output_content:
                return [{"role": "assistant", "content": "I am processing your request. Please wait for the complete response."}], request_id
            else:
                return [{"role": "assistant", "content": output_content}], request_id
        
        elif isinstance(output_content, list):
            # List output - extract text content
            final_response = extract_final_assistant_response(output_content)
            if final_response:
                return [{"role": "assistant", "content": final_response}], request_id
            
            # Fallback: extract any text content
            text_parts = []
            for item in output_content:
                if isinstance(item, dict):
                    if "content" in item:
                        text_parts.append(str(item["content"]))
                    elif "text" in item:
                        text_parts.append(str(item["text"]))
                    elif "output" in item and isinstance(item["output"], str):
                        text_parts.append(str(item["output"]))
                elif isinstance(item, str):
                    text_parts.append(item)
            
            if text_parts:
                return [{"role": "assistant", "content": " ".join(text_parts)}], request_id
    
    # Handle standard chat completions format
    if "messages" in res:
        return res["messages"], request_id
    elif "choices" in res and len(res["choices"]) > 0:
        return [res["choices"][0]["message"]], request_id
    
    # Final fallback
    return [{"role": "assistant", "content": "I received your request but couldn't process the response properly. Please try again."}], request_id


def extract_final_assistant_response(conversation_history):
    """
    Extract the final assistant response from conversation history.
    Handles different response formats from Databricks multi-agent supervisor.
    """
    if not isinstance(conversation_history, list):
        return None
    
    # Look for the last assistant message with actual content
    for item in reversed(conversation_history):
        if not isinstance(item, dict):
            continue
            
        # Check if this is an assistant message
        if item.get("role") == "assistant":
            content = item.get("content")
            if not content:
                continue
                
            # Handle different content formats
            if isinstance(content, str) and content.strip():
                return content
            elif isinstance(content, list):
                # Content array with text items
                text_parts = []
                for content_item in content:
                    if isinstance(content_item, dict):
                        if content_item.get("type") == "output_text":
                            text = content_item.get("text", "")
                            if text.strip():
                                text_parts.append(text)
                        elif "text" in content_item:
                            text = content_item.get("text", "")
                            if text.strip():
                                text_parts.append(text)
                        elif "content" in content_item:
                            text = content_item.get("content", "")
                            if text.strip():
                                text_parts.append(text)
                    elif isinstance(content_item, str) and content_item.strip():
                        text_parts.append(content_item)
                
                if text_parts:
                    return " ".join(text_parts)
    
    return None


def submit_feedback(endpoint, request_id, rating):
    """Submit feedback to the agent."""
    rating_string = "positive" if rating == 1 else "negative"
    text_assessments = [] if rating is None else [{
        "ratings": {
            "answer_correct": {"value": rating_string},
        },
        "free_text_comment": None
    }]

    proxy_payload = {
        "dataframe_records": [
            {
                "source": json.dumps({
                    "id": "e2e-chatbot-app",  # Or extract from auth
                    "type": "human"
                }),
                "request_id": request_id,
                "text_assessments": json.dumps(text_assessments),
                "retrieval_assessments": json.dumps([]),
            }
        ]
    }
    w = WorkspaceClient()
    return w.api_client.do(
        method='POST',
        path=f"/serving-endpoints/{endpoint}/served-models/feedback/invocations",
        body=proxy_payload,
    )


def endpoint_supports_feedback(endpoint_name):
    """Check if the endpoint supports feedback."""
    try:
        w = WorkspaceClient()
        endpoint = w.serving_endpoints.get(endpoint_name)
        return "feedback" in [entity.entity_name for entity in endpoint.config.served_entities]
    except Exception as e:
        print(f"Error checking feedback support: {e}")
        return False
