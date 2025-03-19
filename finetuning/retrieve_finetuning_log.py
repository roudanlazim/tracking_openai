import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API Key from .env file
dotenv_path = os.path.join("C:", os.sep, "Users", "Shaalan", "tracking_openai", "config", ".env")
load_dotenv(dotenv_path=dotenv_path)
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("ERROR: OPENAI_API_KEY not found in environment variables.")  # ✅ Fixed syntax

# Initialize OpenAI Client
client = OpenAI(api_key=api_key)  # ✅ Pass API key

# Fine-tune job ID
job_id = "ftjob-Cu2qrjYZeKu5fR6YHd2NR6M2"

# Retrieve fine-tuning job details
job_details = client.fine_tuning.jobs.retrieve(job_id)
print(job_details)
