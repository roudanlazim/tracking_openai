import openai
import os
from dotenv import load_dotenv

# ✅ Load API Key securely
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ ERROR: OPENAI_API_KEY not found in environment variables.")

openai.api_key = api_key

# ✅ Retrieve a specific fine-tuning job
def get_fine_tuning_job(job_id):
    try:
        job_details = openai.fine_tuning.jobs.retrieve(job_id)  # ✅ Updated API method
        
        print(f"🔍 Fine-Tuning Job Details for ID: {job_id}")
        print(f"Status: {job_details.status}")
        print(f"Model: {job_details.fine_tuned_model if job_details.fine_tuned_model else 'N/A'}")
        print(f"Created At: {job_details.created_at}")

        # ✅ Check if 'updated_at' exists before printing
        if hasattr(job_details, "updated_at"):
            print(f"Updated At: {job_details.updated_at}")

        # ✅ Check if there is a `failure_reason` and print it
        if hasattr(job_details, "error") and job_details.error:
            print(f"❌ Fine-Tuning Failed Reason: {job_details.error}")

        return job_details
    except Exception as e:
        print(f"❌ ERROR: Failed to retrieve fine-tuning job: {str(e)}")
        return None

if __name__ == "__main__":
    job_id = input("Enter Fine-Tuning Job ID: ").strip()
    get_fine_tuning_job(job_id)
