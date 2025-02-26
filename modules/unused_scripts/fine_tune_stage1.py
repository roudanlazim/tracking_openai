import openai
import json
import os
import time
import sys
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ ERROR: OPENAI_API_KEY not found in environment variables.")

openai.api_key = api_key

def show_progress_bar(current_step, total_steps=100):
    """Displays a progress bar that only reaches 100% once."""
    progress = int((current_step / total_steps) * 100)
    bar_length = 30  # Length of the bar
    filled_length = int(bar_length * current_step // total_steps)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    sys.stdout.write(f"\r⏳ Fine-tuning Progress: |{bar}| {progress}% Complete")
    sys.stdout.flush()

def check_fine_tune_status(fine_tune_id):
    """Checks the fine-tuning status periodically and updates the progress bar."""
    print(f"\n🔍 Checking fine-tuning status for ID: {fine_tune_id}")

    status = ""
    progress = 0
    max_checks = 50  # Approximate number of checks before completion

    while status not in ["succeeded", "failed"]:
        response = openai.fine_tuning.jobs.retrieve(fine_tune_id)
        status = response.status  # Correct way to access status
        
        # Estimate progress dynamically (OpenAI doesn’t provide % progress)
        progress = min(progress + (100 // max_checks), 100)  # Ensure it never goes above 100
        show_progress_bar(progress)

        if status in ["succeeded", "failed"]:
            break  # Stop checking once completed

        time.sleep(30)  # Wait time before next check (30s interval)

    print("\n")  # Move to a new line after progress bar
    if status == "succeeded":
        fine_tuned_model = response.fine_tuned_model  # Correct way to get model ID
        print(f"✅ Fine-tuning complete! Model ID: {fine_tuned_model}")
        return fine_tuned_model
    else:
        print("❌ Fine-tuning failed.")
        return None

def fine_tune_model(training_file, log_file="fine_tune_log.txt"):
    """Uploads a training file and starts the fine-tuning process with visual progress tracking."""
    try:
        print(f"📤 Uploading training file: {training_file}")
        
        # Upload the training file
        response = openai.files.create(file=open(training_file, "rb"), purpose='fine-tune')
        file_id = response.id
        print(f"✅ File uploaded successfully. File ID: {file_id}")

        # Start fine-tuning with GPT-3.5 Turbo
        print(f"🚀 Starting fine-tuning process with gpt-3.5-turbo...")
        fine_tune_response = openai.fine_tuning.jobs.create(training_file=file_id, model="gpt-3.5-turbo")
        fine_tune_id = fine_tune_response.id  # Extract the ID correctly

        # Convert the response to a dictionary before writing to JSON
        fine_tune_dict = {
            "file_id": file_id,
            "fine_tune_id": fine_tune_id,
            "status": fine_tune_response.status,
        }

        # Log results
        with open(log_file, "a") as log:
            log.write(f"Fine-tuning started with file ID: {file_id}\n")
            log.write(f"Fine-tune ID: {fine_tune_id}\n")
            log.write(f"Fine-tune response: {json.dumps(fine_tune_dict, indent=2)}\n")

        print(f"🎯 Fine-tuning started! Fine-tune ID: {fine_tune_id}.")
        
        # Start tracking progress properly
        fine_tuned_model = check_fine_tune_status(fine_tune_id)
        return fine_tuned_model

    except Exception as e:
        print(f"❌ ERROR: Fine-tuning failed: {str(e)}")
        return None

if __name__ == "__main__":
    training_jsonl = "data/training_data_stage1.jsonl"  # ✅ Updated for Stage 1 dataset
    fine_tune_model(training_jsonl)
