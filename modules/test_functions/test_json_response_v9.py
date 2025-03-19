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
system_prompt = system_prompt = {
    "role": "developer",
    "content": """
I'm a logistics professional and I handle thousands of shipments every day. I want to be able to tell the progress of a shipment from the list below:

- Manifested
- Collected
- In Transit
- Out for delivery
- On hold
- Delivered
- Returned or Being returned to sender
- Discarded 

Then I will ask you a series of questions to determine what the final status of the shipment is based on the scans I give you. Here's the questions:

If the progress is collected then the final status is 'Collected'.

If the progress of the shipment is 'Manifested', choose one of the following as a sub-status:
- Manifested
- Collection failed
- Collection not attempted
- Collection scheduled

If the sub-status is 'Collection failed', then answer the following questions:

When is the collection rescheduled for? Choose one of the following:
- Collection failed. Another attempt will be made on the next business day
- Collection failed - Now rescheduled. No further information

How many times did the collection fail? Choose one of the following:
- Collection failed once
- Collection failed twice
- Collection failed three or more times

Why did the collection fail? Choose one of the following:
- Collection failed - Over size or weight limits
- Collection failed - Unable to gain access
- Collection failed - Shipper not available
- Collection failed - Parcel not ready
- Collection failed - No further information
- Package not collected - Damaged
- Collection failed or cancelled - Rebooking required

If the sub-status is 'Collection not attempted', then answer the following question:

Why was the collection not attempted? Choose one of the following:
- Directions to the address are required to complete collection
- A correct street name or number is needed for collection
- A correct city or town is needed for collection
- A correct company or receiver name is needed for collection
- A correct suite/apartment number is needed for collection
- Incomplete or incorrect collection address - Additional information or directions required
- Not collected - Address query or error

If the sub-status is 'Collection scheduled', then answer the following question:

When is the collection scheduled for? Choose one of the following:
- Address corrected - Collection will be rescheduled
- Collection scheduled for next business day
- Collection scheduled - No further information

I will give you some scans now. I want you to return:
1. The progress of the shipment
2.- The sub-status
3. The final status based on the questions

Only return one of each and only choose options from the above.

"Return only a JSON object with the following structure: 
{
    \"progress\": \"<Progress>\",
    \"sub_status\": \"<Sub-status>\",
    \"final_status\": \"<Final Status>\"
}
Ensure strict JSON formatting with no additional text or explanation."
 
"""
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