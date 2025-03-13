import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from modules.json_handler import save_json

# Load API Key
load_dotenv(dotenv_path=os.path.join("config", ".env"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define function
def get_ai_progress(messages, model="gpt-4o-mini"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        response_json = json.loads(response.choices[0].message.content)

        # Extract token usage details, including cached tokens
        total_prompt_tokens = response.usage.prompt_tokens
        cached_tokens = getattr(response.usage.prompt_tokens_details, "cached_tokens", 0)  # Ensure fallback to 0
        dynamic_message_tokens = total_prompt_tokens - cached_tokens  # Tokens used in actual conversation

        token_usage = {
            "prompt_tokens": total_prompt_tokens,  # Total tokens used for the full prompt
            "cached_tokens": cached_tokens,  # Tokens served from cache
            "dynamic_message_tokens": dynamic_message_tokens,  # Non-cached prompt tokens
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        output = {
            "response": response_json,
            "token_usage": token_usage,
            "model_used": response.model,
            "created_at": response.created,
            "request_id": response.id
        }

        save_json(output)
        print(json.dumps(output, indent=2))
        return response_json

    except Exception as e:
        print(f"An error occurred: {e}")

# Structured system prompt (clear instruction to choose one status)
system_prompt = {
    "role": "system",
    "content": """You are a logistics AI that determines shipment statuses.
Rules:
- If collected is true then { "p": 2, "s": 2, "f": 2 }
- If collected is false and attempted is false then { "p": 1, "s": 1, "f": 1 }
- If collected is false, attempted is true, and failed is true then { "p": 1, "s": 3, "f": 7 }
Ensure: p=2 only if a collection scan exists.

Mappings:
progress: 1=Manifested, 2=Collected, 3=In Transit, 4=Out for Delivery, 5=On Hold, 6=Delivered, 7=Returned, 8=Discarded.
sub_status: 1=Manifested, 2=Collection Scheduled, 3=Collection Failed, 4=Not Collected.
final_status: 1="Manifested - Awaiting Collection", 2="Address Corrected - Collection Rescheduled",
3="Collection Scheduled - Next Business Day", 4="Collection Scheduled - No Further Info",
5="Collection Failed - Another Attempt Next Day", 6="Collection Failed - Rescheduled, No Info",
7="Collection Failed - Rebooking Required", 8="Collection Failed - Oversized",
9="Collection Failed - Access Issue", 10="Collection Failed - Shipper Unavailable",
11="Collection Failed - Parcel Not Ready", 12="Collection Failed - No Info",
13="Collection Failed - Package Damaged", 14="Collection Not Attempted - Directions Required",
15="Collection Not Attempted - Address Query/Error".

Return only a JSON object with keys p, s, and f. For example: { "p": 1, "s": 3, "f": 5 }."""
}
# User-provided shipment scans
user_message = {
    "role": "user",
    "content": (
        "(2024-09-06T06:40:00) Collection scheduled,(2024-09-05T15:39:04) Collection failed,(2024-09-05T06:48:00) Collection scheduled,(2024-09-04T15:40:01) Collection failed,(2024-09-04T06:20:00) Collection scheduled,(2024-09-03T17:36:51) Shipment manifested"
    )
}

if __name__ == "__main__":
    # First interaction with correct prompts
    messages = [system_prompt, user_message]
    get_ai_progress(messages=messages, model="gpt-4o-mini")

    # Follow-up question maintaining context
    followup_message = {
        "role": "user",
        "content": "Same question as before"
    }
    messages.append(followup_message)
    get_ai_progress(messages=messages, model="gpt-4o-mini")