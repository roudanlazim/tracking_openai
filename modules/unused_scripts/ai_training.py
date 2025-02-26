import openai
import json
import pandas as pd
import os
import time
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

# Load environment variables (for OpenAI API key)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load valid statuses from JSON file
def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

# Step 1: Generate Training and Test Data
def generate_training_data(input_csv, train_csv, test_csv, test_size=0.2):
    df = pd.read_csv(input_csv)
    train, test = train_test_split(df, test_size=test_size, random_state=42)

    train.to_csv(train_csv, index=False)
    test.to_csv(test_csv, index=False)

    print(f"✅ Training data saved to {train_csv}")
    print(f"✅ Test data saved to {test_csv}")

# Step 2: Prepare Training Data for OpenAI Fine-tuning
def prepare_training_data(input_csv, output_jsonl, status_elements_file):
    df = pd.read_csv(input_csv)

    # Load valid statuses
    valid_statuses = load_json(status_elements_file)

    with open(output_jsonl, "w") as f:
        for _, row in df.iterrows():
            ai_story = row["AiStory"].strip()
            correct_status = row["Status"].strip()

            # Ensure the status is valid
            if correct_status not in valid_statuses:
                print(f"⚠️ Warning: Status '{correct_status}' is not in the valid status list. Skipping this entry.")
                continue

            entry = {"messages": [
                {"role": "user", "content": ai_story},
                {"role": "assistant", "content": correct_status}
            ]}
            f.write(json.dumps(entry) + "\n")

    print(f"✅ Training data saved to {output_jsonl}")

# Step 3: Fine-tune Model
def fine_tune_model(training_file, log_file="fine_tune_log.txt"):
    response = openai.File.create(file=open(training_file, "rb"), purpose='fine-tune')
    file_id = response["id"]

    fine_tune_response = openai.FineTune.create(training_file=file_id, model="davinci")  # Using davinci for fine-tuning
    fine_tune_id = fine_tune_response["id"]

    with open(log_file, "a") as log:
        log.write(f"Fine-tuning started with file ID: {file_id}\n")
        log.write(f"Fine-tune ID: {fine_tune_id}\n")
        log.write(f"Fine-tune response: {json.dumps(fine_tune_response, indent=2)}\n")

    print(f"🚀 Fine-tuning started! Fine-tune ID: {fine_tune_id}. Check status using OpenAI dashboard.")
    return fine_tune_id

# Step 4: Check Fine-tuning Status
def check_fine_tune_status(fine_tune_id):
    while True:
        response = openai.FineTune.retrieve(fine_tune_id)
        status = response["status"]
        print(f"Fine-tune status: {status}")

        if status in ["succeeded", "failed"]:
            break
        time.sleep(30)  # Check every 30 seconds

    if status == "succeeded":
        fine_tuned_model = response["fine_tuned_model"]
        print(f"✅ Fine-tuning complete! Model ID: {fine_tuned_model}")
        return fine_tuned_model
    else:
        print("❌ Fine-tuning failed.")
        return None

# Step 5: Use Fine-tuned Model for Prediction
def predict_status(ai_story, fine_tuned_model, valid_statuses_file, results_log="predictions_log.csv"):
    # Load valid statuses
    valid_statuses = load_json(valid_statuses_file)

    response = openai.ChatCompletion.create(
        model=fine_tuned_model,
        messages=[{"role": "system", "content": "You are a logistics assistant."},
                  {"role": "user", "content": ai_story}],
        logprobs=True
    )

    predicted_status = response["choices"][0]["message"]["content"].strip()

    # Validate the predicted status
    if predicted_status not in valid_statuses:
        final_status = "FLAGGED: Invalid prediction"
    else:
        final_status = predicted_status

    with open(results_log, "a") as log:
        log.write(f"{ai_story},{final_status}\n")

    return final_status

if __name__ == "__main__":
    input_csv = "data/training_dataset_ai_stories.csv"
    train_csv = "data/train.csv"
    test_csv = "data/test.csv"
    training_jsonl = "data/training_data.jsonl"
    status_elements_file = "data/status_elements.json"

    generate_training_data(input_csv, train_csv, test_csv)
    prepare_training_data(train_csv, training_jsonl, status_elements_file)

    fine_tune_id = fine_tune_model(training_jsonl)
    fine_tuned_model = check_fine_tune_status(fine_tune_id)

    if fine_tuned_model:
        test_story = "At first, it was Shipment collected, then it was Out for delivery, then it was Delivered to postbox."
        print("Predicted Status:", predict_status(test_story, fine_tuned_model, status_elements_file))
