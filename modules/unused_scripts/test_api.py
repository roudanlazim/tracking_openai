import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print(f"✅ API Key Loaded Successfully: {api_key[:10]}********")
else:
    print("❌ API Key NOT Found!")
