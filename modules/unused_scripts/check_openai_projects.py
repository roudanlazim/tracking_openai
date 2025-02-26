import openai
import os
from dotenv import load_dotenv

# ✅ Load API Key securely
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ ERROR: OPENAI_API_KEY not found in environment variables.")

openai.api_key = api_key

def list_openai_organizations():
    """Lists all organizations linked to this OpenAI account."""
    try:
        orgs = openai.organizations.list()  # ✅ Correct API method for retrieving organizations

        if not orgs.data:
            print("ℹ️ No organizations found for this API key.")
        else:
            print("🔍 OpenAI Organizations:")
            for org in orgs.data:
                print(f"🆔 Organization ID: {org.id}, Name: {org.name}")

    except Exception as e:
        print(f"❌ ERROR: Failed to retrieve organizations: {str(e)}")

if __name__ == "__main__":
    list_openai_organizations()
