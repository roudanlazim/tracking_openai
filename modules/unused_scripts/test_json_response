import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Correctly load your .env file
load_dotenv(dotenv_path=os.path.join("config", ".env"))

# initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_progress(messages, model="gpt-4o-mini"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,
            response_format={"type": "json_object"}  # Ensure JSON response
        )

        # Access message content directly
        response_json = json.loads(response.choices[0].message.content)
        progress_value = response_json.get("progress", None)

        print("Progress:", progress_value)

    except json.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
        print("Raw response:", response.choices[0].message.content)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that returns only valid JSON. Your JSON must include a top-level key 'progress'."
        },
        {
            "role": "user",
            "content": "The shipment is stuck in customs clearance since yesterday. Provide the current progress status."
        }
    ]

    get_ai_progress(messages=messages, model="gpt-4o-mini")