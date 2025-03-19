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
        "You are an assistant that returns only valid JSON. "
        "Your JSON must contain exactly one key: 'progress', representing the current status of the shipment. "
        "Select the status that best describes the current shipment situation from the following list:\n"
        "1. Delivered: Shipment successfully delivered to recipient or safe location.\n"
        "2. Damaged: Shipment damaged during transit or handling.\n"
        "3. Lost: Shipment missing and considered lost.\n"
        "4. On Hold: Shipment on hold due to a general issue or delay.\n"
        "5. In Transit: Shipment actively moving towards destination.\n"
        "6. Customs Delay: Held at customs for clearance issues.\n"
        "7. Returned: Shipment is returning to sender due to issues.\n"
        "8. Exception: Shipment encountered a critical issue causing delay.\n"
        "9. Attempted Delivery: Courier attempted but failed to deliver shipment.\n"
        "10. Held for Collection: Shipment available at collection point.\n"
        "11. Collection Failed: Recipient failed to collect shipment."
    )
}

# User-provided shipment scans (Example)
user_message = {
    "role": "user",
    "content": (
        "(2024-09-26T07:05:00) Delivery attempted,"
        "(2024-09-12T04:46:00) Delivery attempted,"
        "(2024-09-11T22:39:00) Delivery attempted,"
        "(2024-09-11T01:26:00) Arrival at delivery depot,"
        "(2024-09-06T08:44:00) In Transit,"
        "(2024-09-05T07:19:00) Export Scan,"
        "(2024-09-05T03:20:00) Warehouse Scan"
    )
}

if __name__ == "__main__":
    # First interaction with correct prompts
    messages = [system_prompt, user_message]
    get_ai_progress(messages=messages, model="gpt-4o-mini")

    # Follow-up question maintaining context
    followup_message = {
        "role": "user",
        "content": "How long do shipments typically remain at the depot after an attempted delivery?"
    }
    messages.append(followup_message)
    get_ai_progress(messages=messages, model="gpt-4o-mini")