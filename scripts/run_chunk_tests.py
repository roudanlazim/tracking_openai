import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI
from modules.mongo_handler import fetch_filtered_shipments, store_ai_results
from modules.prompt_generator import generate_prompt
from modules.json_handler import load_json, save_json
from modules.user_input import select_prompt

load_dotenv(dotenv_path=os.path.join("config", ".env"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_progress(messages, model="gpt-4o-mini", retries=3):
    """
    Sends multiple shipments in one request and expects a structured JSON response
    wrapped in an object.
    """
    for attempt in range(retries):
        try:
            print(f"\n🚀 Attempt {attempt + 1}: Sending batch to GPT...")
            print("🔍 Messages Sent:", messages)  # Debug Print

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.0,
                response_format={"type": "json_object"}  # ✅ Ensure JSON object response
            )

            print(f"✅ Raw OpenAI Response: {response}")  # Debug Print

            # ✅ Correct way to access response
            response_json = response.choices[0].message.content

            # Convert the response from a string to a JSON object
            response_json = json.loads(response_json)

            if "shipments" in response_json and isinstance(response_json["shipments"], list):
                return response_json["shipments"]

            print("⚠️ AI response did not contain expected 'shipments' key.")
            return None

        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1}: {e}")
            time.sleep((attempt + 1) * 2)

    print("❌ GPT API failed after multiple retries. Skipping this batch.")
    return None

if __name__ == "__main__":
    selected_prompt_file = select_prompt()
    system_prompt_json = load_json(selected_prompt_file)
    if system_prompt_json is None:
        raise FileNotFoundError(f"❌ Prompt file '{selected_prompt_file}' not found or invalid.")

    shipments = fetch_filtered_shipments("your_input_collection", batch_size=5)
    if not shipments:
        print("⚠️ No valid shipments to process.")
        exit(0)

    messages = generate_prompt(shipments, selected_prompt_file)
    ai_responses = get_ai_progress(messages)

    if ai_responses and len(ai_responses) == len(shipments):  # ✅ Ensure proper mapping
        for shipment, ai_response in zip(shipments, ai_responses):
            shipment["ai_analysis"] = ai_response  # ✅ Attach AI response

        store_ai_results("ai_predictions", shipments)
        print(f"\n✅ Successfully processed and stored {len(shipments)} shipments.")
    else:
        print("\n⚠️ AI responses did not match the number of shipments. Skipping storage.")
