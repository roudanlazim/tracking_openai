import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from openai._exceptions import APIError, APIConnectionError, RateLimitError

# load .env file
dotenv_path = os.path.join("C:", os.sep, "Users", "Shaalan", "tracking_openai", "config", ".env")
load_dotenv(dotenv_path=dotenv_path)

# Retrieve API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("ERROR: OPENAI_API_KEY not found in environment variables. Check your .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def select_training_file(directory):
    """Prompt user to select a training file from a directory."""
    files = [f for f in os.listdir(directory) if f.endswith(".jsonl")]
    if not files:
        raise ValueError(f"No .jsonl files found in {directory}")

    print("\nAvailable training files:")
    for idx, file in enumerate(files, 1):
        print(f"{idx}. {file}")

    while True:
        try:
            choice = int(input("Select a training file (enter number): ")) - 1
            if 0 <= choice < len(files):
                selected_file = os.path.join(directory, files[choice])
                print(f"Selected training file: {selected_file}")
                return selected_file
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def validate_jsonl(training_file):
    """Validates JSONL training file format."""
    print(f"Validating JSONL file: {training_file}")
    with open(training_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON at line {i}: {e}")
    print("JSONL validation passed.")

def upload_with_retry(file_path, max_retries=5):
    """Uploads file to OpenAI with retry logic."""
    for attempt in range(max_retries):
        try:
            with open(file_path, "rb") as file_fd:
                file_id = client.files.create(file=file_fd, purpose="fine-tune").id
            print(f"File uploaded successfully. File ID: {file_id}")
            return file_id
        except RateLimitError:
            wait_time = 2 ** attempt
            print(f"Rate limit hit. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        except APIError as e:
            print(f"OpenAI API Error: {e}")
            break
    raise RuntimeError("Max retries reached. Upload failed.")

def fine_tune_model(training_file, base_model="gpt-4o-mini-2024-07-18", log_file="fine_tune_log.txt"):
    validate_jsonl(training_file)

    try:
        # Upload training file
        file_id = upload_with_retry(training_file)

        # Start fine-tuning process
        print(f"Starting fine-tuning with base model '{base_model}'...")
        fine_tune_job = client.fine_tuning.jobs.create(
            training_file=file_id,
            model=base_model,
            suffix="v8_shaalan_2025"
        )
        fine_tune_id = fine_tune_job.id
        print(f"Fine-tuning job started. Job ID: {fine_tune_id}")

        # Monitor job status
        while True:
            job_status = client.fine_tuning.jobs.retrieve(fine_tune_id)
            print(f"Job Status: {job_status.status}")

            if job_status.status in ["succeeded", "failed", "cancelled"]:
                break

            time.sleep(10)  # Check status every 20 seconds

        if job_status.status == "succeeded":
            fine_tuned_model_name = job_status.fine_tuned_model
            print(f"Fine-tuning job completed! Model Name: {fine_tuned_model_name}")

            # Save model name
            with open("fine_tuned_model.txt", "w") as f:
                f.write(fine_tuned_model_name)

        # Log response
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"Fine-tuning job started:\n")
            log.write(f"File ID: {file_id}\n")
            log.write(f"Job ID: {fine_tune_id}\n")
            log.write(f"Response: {json.dumps(job_status.model_dump(), indent=2)}\n\n")

    except APIConnectionError:
        print("The server could not be reached.")
    except RateLimitError:
        print("A 429 status code was received.")
    except APIError as e:
        print(f"Fine-tuning failed. API Error: {str(e)}")

if __name__ == "__main__":
    training_dir = r"C:\Users\Shaalan\tracking_openai\data\training"
    training_jsonl = select_training_file(training_dir)
    fine_tune_model(training_file=training_jsonl)