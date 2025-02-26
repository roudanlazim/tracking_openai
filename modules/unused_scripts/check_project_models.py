import openai
import os
from dotenv import load_dotenv

# ✅ Load API Key securely
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ ERROR: OPENAI_API_KEY not found in environment variables.")

openai.api_key = api_key

def get_model_details(model_id):
    """Retrieves detailed information for a specific fine-tuned model."""
    try:
        model_details = openai.models.retrieve(model_id)
        print(f"🔍 Model Details for {model_id}:")
        print(f"📌 Owned By: {model_details.owned_by}")
        print(f"📆 Created At: {model_details.created}")
        print(f"🔗 Permissions: {model_details.permission}")
    except Exception as e:
        print(f"❌ ERROR: Failed to retrieve model: {str(e)}")

if __name__ == "__main__":
    model_id = input("Enter Fine-Tuned Model ID: ").strip()
    get_model_details(model_id)
