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

    # For multi-agent supervisor endpoints, use the input format
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
    w = WorkspaceClient()
    endpoint = w.serving_endpoints.get(endpoint_name)
    return "feedback" in [entity.entity_name for entity in endpoint.config.served_entities] 
def query_endpoint(endpoint_name, messages, max_tokens, return_traces):
    """
    Query an endpoint, returning the string message content and request
    ID for feedback
    """
    """Calls a model serving endpoint."""
    
    # For multi-agent supervisor endpoints, use the 'input' format
    # For multi-agent supervisor endpoints, use the input format
    # Extract the user message from the messages array
    user_message = ""
    for msg in messages:
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    # Prepare input payload for multi-agent supervisor
    # The endpoint expects a Message object with role and content
    inputs = {
        "input": [{"role": "user", "content": user_message}],
        "max_output_tokens": max_tokens,
    }
    
    if return_traces:
        inputs["databricks_options"] = {"return_trace": True}
    
    res = get_deploy_client('databricks').predict(
        endpoint=endpoint_name,
        inputs=inputs,
    )
    
    try:
        res = get_deploy_client('databricks').predict(
            endpoint=endpoint_name,
            inputs=inputs,
        )
    except Exception as e:
        print(f"DEBUG: Error calling multi-agent supervisor: {e}")
        return [{"role": "assistant", "content": "I encountered an issue while processing your request. The system is currently experiencing some difficulties. Please try again in a moment or contact support if the issue persists."}], None
    
    # Extract request_id with fallback to None
    request_id = res.get("databricks_output", {}).get("databricks_request_id") if res else None
    
    # Debug: log the response
    print("DEBUG: Response received:", res)
    
    # Check for handoff messages early
    if isinstance(res, dict):
        for key, value in res.items():
            if isinstance(value, str) and "Handed off to:" in value:
                print("DEBUG: Found handoff message in", key)
                return [{"role": "assistant", "content": "I am processing your request. Please wait for the complete response."}], request_id
        
        # Check for the specific response format we are seeing
        if res.get("object") == "response" and "output" in res:
            output_list = res["output"]
            if isinstance(output_list, list):
                for item in output_list:
                    if isinstance(item, dict) and item.get("type") == "function_call_output":
                        output_text = item.get("output", "")
                        if "Handed off to:" in output_text:
                            print("DEBUG: Found function call output handoff message")
                            return [{"role": "assistant", "content": "I am processing your request. Please wait for the complete response."}], request_id
                        elif "Error" in output_text or "error" in output_text.lower():
                            print("DEBUG: Found error in function call output")
                            return [{"role": "assistant", "content": "I encountered an issue while processing your request. Please try again in a moment."}], request_id
    
    # Handle different response formats based on Databricks multi-agent supervisor patterns
    if "input" in res:
        # Multi-agent supervisor returns conversation history in 'input' field
        conversation_history = res["input"]
        
        if isinstance(conversation_history, list):
            # Extract the final assistant response from conversation history
            final_response = extract_final_assistant_response(conversation_history)
            if final_response:
                return [{"role": "assistant", "content": final_response}], request_id
    
    # Handle output field responses (common in multi-agent supervisors)
    if "output" in res:
        output_content = res["output"]
        
        # If output is a string, check if it's a handoff message
        if isinstance(output_content, str):
            if "Handed off to:" in output_content:
                print("DEBUG: Found handoff message in output string")
                return [{"role": "assistant", "content": "I am processing your request. Please wait for the complete response."}], request_id
            else:
                return [{"role": "assistant", "content": output_content}], request_id
        
        # If output is a list, look for the final response
        elif isinstance(output_content, list):
            # Look for the last assistant message with actual content
            final_response = extract_final_assistant_response(output_content)
            if final_response:
                return [{"role": "assistant", "content": final_response}], request_id
            
            # Fallback: try to extract any text content
            text_parts = []
            for item in output_content:
                if isinstance(item, dict):
                    if "content" in item:
                        text_parts.append(str(item["content"]))
                    elif "text" in item:
                        text_parts.append(str(item["text"]))
                    elif "output" in item and isinstance(item["output"], str):
                        # Handle function call outputs that might contain the final response
                        text_parts.append(str(item["output"]))
                    else:
                        text_parts.append(str(item))
                else:
                    text_parts.append(str(item))
            if text_parts:
                return [{"role": "assistant", "content": " ".join(text_parts)}], request_id
        
        # If output is a dict, check for specific patterns
        elif isinstance(output_content, dict):
            if output_content.get("type") == "function_call_output":
                # This is a handoff message, return a processing message
                return [{"role": "assistant", "content": "I am processing your request. Please wait for the complete response."}], request_id
            elif "content" in output_content:
                return [{"role": "assistant", "content": str(output_content["content"])}], request_id
            elif "text" in output_content:
                return [{"role": "assistant", "content": str(output_content["text"])}], request_id
    
    if "messages" in res:
        return res["messages"], request_id
    elif "choices" in res:
        return [res["choices"][0]["message"]], request_id
    
    # Final fallback - return a generic message
    return [{"role": "assistant", "content": "I received your request but couldn't process the response properly. Please try again."}], request_id


def extract_final_assistant_response(conversation_history):
    """
    Extract the final assistant response from conversation history.
    Based on Databricks multi-agent supervisor response patterns.
    """
    if not isinstance(conversation_history, list):
        return None
    
    # Look for the last assistant message with actual content
    for item in reversed(conversation_history):
        if not isinstance(item, dict):
            continue
            
        # Check if this is an assistant message
        if item.get("role") == "assistant" and item.get("type") == "message":
            content = item.get("content")
            if not content:
                continue
                
            # Handle different content formats
            if isinstance(content, str):
                # Direct string content
                if content.strip():
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
    w = WorkspaceClient()
    endpoint = w.serving_endpoints.get(endpoint_name)
    return "feedback" in [entity.entity_name for entity in endpoint.config.served_entities]
