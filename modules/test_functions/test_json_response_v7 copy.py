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
    "You are a logistics assistant who determines shipment statuses based on provided scans. "
    "Use the decision tree below to assign numerical codes for progress, sub-status, and final status.\n\n"

    "**Response Format:**\n"
    "{\n"
    "  \"p\": <Progress Code>,\n"
    "  \"s\": <Sub-status Code>,\n"
    "  \"f\": <Final Status Code>\n"
    "}\n\n"

    "**Valid Codes:**\n"
    "- `p=1-8` (Progress)\n"
    "- `s=1-4` (Sub-status)\n"
    "- `f=1-15` (Final Status)\n\n"

    "**Rules for Assigning Progress (`p`):**\n"
    "- `p=2` (Collected) can **only** be assigned if there is a scan explicitly confirming collection.\n"
    "- If collection has been attempted but failed, the progress must remain `p=1` (Manifested).\n"
    "- If there is no scan confirming successful collection, `p=2` must **never** be used.\n\n"

    "**Decision Logic:**\n"
    "1. Has the shipment been collected? (Confirmed by scan)\n"
    "   - Yes → `p=2, s=2, f=2`\n"
    "   - No → `p=1`, proceed to step 2\n\n"

    "2. Has collection been attempted?\n"
    "   - No → `s=1, f=1`\n"
    "   - Yes → Proceed to step 3\n\n"

    "3. Select Sub-status (`s`) and Final Status (`f`):\n"
    "   - `s=1` → `f=1`\n"
    "   - `s=2` → `f=2, 3, or 4`\n"
    "   - `s=3` (Collection Failed) →\n"
    "       - If cancellation or rebooking required → `f=7`\n"
    "       - Otherwise → `f=5 or 6`\n"
    "   - `s=4` → `f=14 or 15`\n\n"

    "Ensure that `p=2` is **never** used unless a collection confirmation scan is present. "
    "If collection has only been attempted or failed, `p=1` must always be used."
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