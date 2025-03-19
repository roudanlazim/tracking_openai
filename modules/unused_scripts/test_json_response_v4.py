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

        token_usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
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
        "I'm a logistics professional and handle thousands of shipments every day. Based on the shipment scans I provide, you will determine the shipment status using the decision-tree below.\n\n"

        "Always return your response strictly formatted as:\n"
        "{\n"
        "  'progress': '<Progress>',\n"
        "  'sub-status': '<Sub-status>',\n"
        "  'final status': '<Final Status>'\n"
        "}\n\n"

        "Valid Progress Statuses:\n"
        "- Manifested\n"
        "- Collected\n"
        "- In Transit\n"
        "- Out for delivery\n"
        "- On hold\n"
        "- Delivered\n"
        "- Returned or Being returned to sender\n"
        "- Discarded\n\n"

        "Decision Tree:\n\n"

        "Q1: Has the shipment been collected?\n"
        "- YES → progress = 'Collected', sub-status = 'Collected', final status = 'Collected'\n"
        "- NO → progress = 'Manifested', proceed to Q2\n\n"

        "Q2: Has collection been attempted?\n"
        "- NO → sub-status = 'Manifested', final status = 'Shipment manifested - Awaiting collection'\n"
        "- YES → Move to Q2\n\n"

        "Q2: Select sub-status from these numbered options:\n"
        "1. Manifested\n"
        "2. Collection scheduled\n"
        "3. Collection failed\n"
        "4. Collection not attempted\n\n"

        "- If 'Manifested' selected (1):\n"
        "  → final status = 'Manifested'\n\n"

        "- If 'Collection scheduled' (2), select exact final status:\n"
        "   1. Address corrected - Collection will be rescheduled\n"
        "   2. Collection scheduled for next business day\n"
        "   3. Collection scheduled - No further information\n\n"

        "- If 'Collection failed' (3), answer:\n"
        "   A. Next collection attempt:\n"
        "      1. Another attempt will be made on the next business day\n"
        "      2. Collection failed - Now rescheduled. No further information\n"
        "   3. Collection failed or cancelled. Rebooking required\n\n"

        "   B. Number of failed attempts:\n"
        "   1. Collection failed once\n"
        "   2. Collection failed twice\n"
        "   3. Collection failed three or more times\n\n"

        "   C. Reason for failure:\n"
        "   1. Collection failed - Over size or weight limits\n"
        "   2. Collection failed - Unable to gain access\n"
        "   3. Collection failed - Shipper not available\n"
        "   4. Collection failed - Parcel not ready\n"
        "   5. Collection failed - No further information\n"
        "   6. Package not collected - Damaged\n"
        "   7. Collection failed or cancelled - rebooking required\n\n"

        "- If 'Collection not attempted', select exact reason:\n"
        "   1. Directions to the address are required to complete collection\n"
        "   2. A correct street name or number is needed for collection\n"
        "   3. A correct city or town is needed for collection\n"
        "   4. A correct company or receiver name is needed for collection\n"
        "   5. A correct suite/apartment number is needed for collection\n"
        "   6. Incomplete or incorrect collection address - Additional information or directions required\n"
        "   6. Not collected - Address query or error\n\n"

        "Q3: In your JSON response, explicitly state your chosen numbered selections as provided above.\n"
        "Always follow this structured decision tree exactly."
    )
}

# User-provided shipment scans (Example)
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