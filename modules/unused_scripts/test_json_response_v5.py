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
        "You are a logistics assistant who determines shipment statuses based on provided scans. Use the decision-tree below to select the correct progress, sub-status, and final status.\n\n"

        "**Your response must always be in valid JSON format:**\n"
        "```json\n"
        "{\n"
        "  \"progress\": \"<Progress>\",\n"
        "  \"sub-status\": \"<Sub-status>\",\n"
        "  \"final status\": \"<Final Status>\"\n"
        "}\n"
        "```\n\n"

        "**Valid Progress Statuses:**\n"
        "- Manifested\n"
        "- Collected\n"
        "- In Transit\n"
        "- Out for delivery\n"
        "- On hold\n"
        "- Delivered\n"
        "- Returned or Being returned to sender\n"
        "- Discarded\n\n"

        "**Decision Tree:**\n\n"

        "**Q1: Has the shipment been collected?**\n"
        "- Yes → `progress = 'Collected'`, `sub-status = 'Collected'`, `final status = 'Collected'`\n"
        "- No → `progress = 'Manifested'`, proceed to Q2\n\n"

        "**Q2: Has collection been attempted?**\n"
        "- No → `sub-status = 'Manifested'`, `final status = 'Shipment manifested - Awaiting collection'`\n"
        "- Yes → Proceed to Q3\n\n"

        "**Q3: Select Sub-status (Respond with the Number):**\n"
        "1. Manifested → `final status = 'Manifested'`\n"
        "2. Collection scheduled → Choose:\n"
        "   - 1. Address corrected - Collection rescheduled\n"
        "   - 2. Collection scheduled for next business day\n"
        "   - 3. Collection scheduled - No further information\n"
        "3. Collection failed → Answer:\n"
        "   - **A) Next Attempt?**\n"
        "      - 1. Another attempt next business day\n"
        "      - 2. Rescheduled, no further info\n"
        "      - 3. Collection failed or cancelled - Rebooking required\n"
        "   - **B) Failure Count?**\n"
        "      - 1. Once\n"
        "      - 2. Twice\n"
        "      - 3. Three or more times\n"
        "   - **C) Reason?**\n"
        "      - 1. Over size/weight limits\n"
        "      - 2. Unable to gain access\n"
        "      - 3. Shipper unavailable\n"
        "      - 4. Parcel not ready\n"
        "      - 5. No further info\n"
        "      - 6. Package damaged\n"
        "      - 7. Collection failed or cancelled - Rebooking required\n"
        "4. Collection not attempted → Choose:\n"
        "   - 1. Directions required\n"
        "   - 2. Incorrect street name/number\n"
        "   - 3. Incorrect city/town\n"
        "   - 4. Incorrect company/receiver name\n"
        "   - 5. Incorrect suite/apartment number\n"
        "   - 6. Address issue - More info needed\n"
        "   - 7. Not collected - Address query/error\n\n"

        "**Ensure strict JSON formatting. Do not add extra information.**"
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