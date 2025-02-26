import openai
import os
from dotenv import load_dotenv

# ✅ Load API Key securely
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ ERROR: OPENAI_API_KEY not found in environment variables.")

openai.api_key = api_key

# ✅ List all fine-tuning jobs
try:
    fine_tuning_jobs = openai.fine_tuning.jobs.list()  # ✅ Updated API method

    if not fine_tuning_jobs.data:  # ✅ Updated to access response correctly
        print("ℹ️ No fine-tuning jobs found.")
    else:
        print("🔍 Fine-Tuning Jobs:")
        for job in fine_tuning_jobs.data:
            print(f"ID: {job.id}, Status: {job.status}, Model: {job.fine_tuned_model if job.fine_tuned_model else 'N/A'}")

except Exception as e:
    print(f"❌ ERROR: Failed to retrieve fine-tuning jobs: {str(e)}")
