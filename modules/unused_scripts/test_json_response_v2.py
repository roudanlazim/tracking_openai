import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file from config directory
load_dotenv(dotenv_path=os.path.join("config", ".env"))

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to call OpenAI and maintain conversation state
def get_ai_progress(messages, model="gpt-4o-mini"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        # Parse JSON response from assistant
        response_json = json.loads(response.choices[0].message.content)

        # Extract basic token usage details
        usage = response.usage
        token_usage = {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        }

        # Detailed token info (convert explicitly to dict)
        prompt_tokens_details = {
            "cached_tokens": usage.prompt_tokens_details.cached_tokens,
            "audio_tokens": usage.prompt_tokens_details.audio_tokens,
        }

        completion_tokens_details = {
            "reasoning_tokens": usage.completion_tokens_details.reasoning_tokens,
            "audio_tokens": usage.completion_tokens_details.audio_tokens,
            "accepted_prediction_tokens": usage.completion_tokens_details.accepted_prediction_tokens,
            "rejected_prediction_tokens": usage.completion_tokens_details.rejected_prediction_tokens,
        }

        # Prepare fully serializable output
        output = {
            "response": response_json,
            "token_usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "prompt_tokens_details": prompt_tokens_details,
                "completion_tokens_details": completion_tokens_details,
            },
            "model_used": response.model,
            "created_at": response.created,
            "request_id": response.id
        }

        print(json.dumps(output, indent=2))

        return response_json

    except json.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
        print("Raw response:", response.choices[0].message.content)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that returns only valid JSON. "
                "Your JSON must include a top-level key 'progress'."
                
            )
        },
        {
            "role": "user",
            "content": (
                "(2024-09-26T07:05:00) Delivery attempted,(2024-09-12T04:46:00) Delivery attempted,(2024-09-11T22:39:00) Delivery attempted,(2024-09-26T07:05:00) Delivery attempted,(2024-09-12T04:46:00) Delivery attempted,(2024-09-11T22:39:00) Delivery attempted,(2024-09-11T01:26:00) Arrival at delivery depot,(2024-09-06T08:44:00) In Transit,(2024-09-05T08:31:00) Arrival scan,(2024-09-05T07:19:00) In Transit,(2024-09-05T07:19:00) Export Scan,(2024-09-05T03:20:00) Warehouse Scan,(2024-09-05T01:12:00) Warehouse Scan,(2024-09-05T01:00:00) In Transit"
                "Provide the current progress status."
            )
        }
    ]

    # First interaction
    get_ai_progress(messages=messages, model="gpt-4o-mini")

    # Adding follow-up question to maintain state
    messages.append({
        "role": "user",
        "content": "How long do shipments usually stay in customs?"
    })

    # Second call, maintaining conversation state
    get_ai_progress(messages=messages, model="gpt-4o-mini")