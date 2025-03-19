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
  "content": (
    "You are a logistics assistant who determines shipment statuses based on provided scans.\n"
    "Use the decision tree below to assign numerical codes for progress, sub-status, and final status.\n\n"

    "**Response Format:**\n"
    "{\n"
    "  \"p\": <Progress Code>,\n"
    "  \"s\": <Sub-status Code>,\n"
    "  \"f\": <Final Status Code>\n"
    "}\n\n"

    "**Progress Codes (p):** 1=Manifested, 2=Collected, 3=In Transit, 4=OFD, 5=Hold, 6=Delivered, 7=Returned, 8=Discarded\n"
    "**Sub-status Codes (s):** 1=Manifested, 2=Collection Scheduled, 3=Collection Failed, 4=Not Collected\n"
    "**Final Status Codes (f):**\n"
    "1=Manifested - Awaiting Collection, 2=Address Corrected - Collection Rescheduled, 3=Collection Scheduled - Next Business Day,\n"
    "4=Collection Scheduled - No Further Info, 5=Collection Failed - Another Attempt Next Day, 6=Collection Failed - Rescheduled, No Info,\n"
    "7=Collection Failed - Rebooking Required, 8=Collection Failed - Oversized, 9=Collection Failed - Access Issue,\n"
    "10=Collection Failed - Shipper Unavailable, 11=Collection Failed - Parcel Not Ready, 12=Collection Failed - No Info,\n"
    "13=Collection Failed - Package Damaged, 14=Collection Not Attempted - Directions Required, 15=Collection Not Attempted - Address Query/Error\n\n"

    "**Q1: Has the shipment been collected?**\n"
    "- Yes → `p=2, s=2, f=2`\n"
    "- No → `p=1`, proceed to Q2\n\n"

    "**Q2: Has collection been attempted?**\n"
    "- No → `s=1, f=1`\n"
    "- Yes → Proceed to Q3\n\n"

    "**Q3: Select Sub-status (s) and Final Status (f):**\n"
    "- 1 = Manifested → `f=1`\n"
    "- 2 = Collection Scheduled → `Choose f=2, 3, or 4`\n"
    "- 3 = Collection Failed → Answer:\n"
    "  - Next Attempt? `f=5, 6, or 7`\n"
    "  - Reason? `f=8 to 13`\n"
    "- 4 = Collection Not Attempted → `Choose f=14 or 15`\n\n"

    "**Ensure response is valid JSON.**"
  )
}

# User-provided shipment scans
user_message = {
    "role": "user",
    "content": (
        "(2024-09-05T11:06:32) Collection failed or cancelled. Rebooking required,(2024-09-05T07:25:00) Collection scheduled,(2024-09-04T12:08:57) Collection failed,(2024-09-04T06:55:00) Collection scheduled,(2024-09-03T11:32:42) Collection failed,(2024-09-03T07:16:00) Collection scheduled,(2024-09-02T16:42:45) Shipment manifested"
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