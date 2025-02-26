import openai
import os
from dotenv import load_dotenv

# ✅ Load API Key securely
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ ERROR: OPENAI_API_KEY not found in environment variables.")

openai.api_key = api_key

def list_fine_tuned_models():
    """Lists all fine-tuned models available in the account."""
    try:
        models = openai.models.list()

        if not models.data:
            print("ℹ️ No fine-tuned models found.")
        else:
            print("🔍 Available Fine-Tuned Models:")
            for model in models.data:
                print(f"🆔 Model ID: {model.id}, Owned By: {model.owned_by}")

    except Exception as e:
        print(f"❌ ERROR: Failed to retrieve models: {str(e)}")

if __name__ == "__main__":
    list_fine_tuned_models()
