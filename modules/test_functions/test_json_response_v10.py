import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from modules.json_handler import load_json, save_json
from modules.user_input import select_prompt

# Load environment variables
load_dotenv(dotenv_path=os.path.join("config", ".env"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define function
def get_ai_progress(messages, model="gpt-4o-mini"):
    try:
        print("\nSending to GPT Model:")
        print(json.dumps(messages, indent=2))

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

        # Display the response for debugging
        print("\nOutput Response:")
        print(json.dumps(output, indent=2))

        return response_json

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Prompt user to select a JSON prompt
    selected_prompt_file = select_prompt()  # returns 'data/prompts/system_prompt.json'
    selected_prompt_filename = os.path.basename(selected_prompt_file)

    system_prompt_json = load_json(selected_prompt_filename)

    if system_prompt_json is None:
        raise FileNotFoundError(f"Prompt file '{selected_prompt_filename}' not found or invalid.")

    developer_prompt = {
        "role": "developer",
        "content": "\n".join(system_prompt_json["content"])
    }

    # Example user-provided shipment scans
    user_message = {
        "role": "user",
        "content": (
            "(2024-09-06T06:40:00) Collection scheduled,(2024-09-05T15:39:04) Collection failed,"
            "(2024-09-05T06:48:00) Collection scheduled,(2024-09-04T15:40:01) Collection failed,"
            "(2024-09-04T06:20:00) Collection scheduled,(2024-09-03T17:36:51) Shipment manifested"
        )
    }

    messages = [
        developer_prompt,
        user_message
    ]

    # Initial call
    get_ai_progress(messages=messages, model="gpt-4o-mini")

    # Follow-up question to maintain context
    followup_message = {"role": "user", "content": "Same question as before"}
    messages.append(followup_message)
    get_ai_progress(messages=messages, model="gpt-4o-mini")