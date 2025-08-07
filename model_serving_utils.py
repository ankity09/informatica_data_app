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
    
    request_id = res.get("databricks_output", {}).get("databricks_request_id")
    
    # Handle different response formats
    """
    Poll for the final result from a multi-agent supervisor call
    """
    import time
    
    for attempt in range(max_retries):
        try:
            # Try to get the result using the call_id
            inputs = {
                "call_id": call_id,
                "action": "get_result"
            }
            
            res = get_deploy_client('databricks').predict(
                endpoint=endpoint_name,
                inputs=inputs,
            )
            
            # Check if we have a final result
            if "output" in res:
                output_content = res["output"]
                if isinstance(output_content, dict) and output_content.get("type") != "function_call_output":
                    return output_content
                elif isinstance(output_content, str) and "Handed off to:" not in output_content:
                    return output_content
            
            # Wait before next attempt
            time.sleep(delay)
            
        except Exception as e:
            print(f"Polling attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    
    return None
    
    # Handle different response formats
    if "output" in res:
        # Multi-agent supervisor response format
        output_content = res["output"]
        
        # Check if this is a function call output that needs polling
        if isinstance(output_content, dict) and output_content.get("type") == "function_call_output":
            call_id = output_content.get("call_id")
            handoff_message = output_content.get("output", "")
            
            # For now, return the handoff message with a note about polling
            content = f"{handoff_message}\n\n*Note: This request has been handed off to a specialized assistant. The complete response may require additional processing time.*"
            return [{"role": "assistant", "content": content}], request_id
        
        elif isinstance(output_content, list):
            # If output is a list, try to extract text content
            text_parts = []
            for item in output_content:
                if isinstance(item, dict):
                    # Handle function call outputs
                    if item.get("type") == "function_call_output":
                        handoff_message = item.get("output", "")
                        text_parts.append(f"{handoff_message} (Processing...)")
                    elif "content" in item:
                        text_parts.append(str(item["content"]))
                    elif "text" in item:
                        text_parts.append(str(item["text"]))
                    elif "message" in item:
                        text_parts.append(str(item["message"]))
                    else:
                        text_parts.append(str(item))
                else:
                    text_parts.append(str(item))
            content = " ".join(text_parts)
        else:
            content = str(output_content)
        return [{"role": "assistant", "content": content}], request_id
    elif "messages" in res:
        return res["messages"], request_id
    elif "choices" in res:
        return [res["choices"][0]["message"]], request_id
    else:
        # Fallback: try to extract response from various possible fields
        if "response" in res:
            response_content = res["response"]
            if isinstance(response_content, list):
                content = " ".join([str(item) for item in response_content])
            else:
                content = str(response_content)
            return [{"role": "assistant", "content": content}], request_id
        elif "text" in res:
            text_content = res["text"]
            if isinstance(text_content, list):
                content = " ".join([str(item) for item in text_content])
            else:
                content = str(text_content)
            return [{"role": "assistant", "content": content}], request_id
        else:
            # If we can't find a response, return the raw response as a string
            if isinstance(res, list):
                content = " ".join([str(item) for item in res])
            else:
                content = str(res)
            return [{"role": "assistant", "content": content}], request_id
