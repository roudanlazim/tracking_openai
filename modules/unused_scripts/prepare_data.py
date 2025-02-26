import openai
import pandas as pd
import json
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from utils import load_json

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("❌ ERROR: OPENAI_API_KEY not found in environment variables.")
    raise ValueError("❌ ERROR: OPENAI_API_KEY not found in environment variables.")

client = openai.OpenAI(api_key=api_key)
logging.info(f"🔹 Using API Key: {api_key[:10]}********")  # Mask API Key for security

# Define ignored scans
IGNORED_SCANS = {"Shipment Manifested", "Billing Information Received", "Internal Scan"}

# Define resolving scans
RESOLVING_SCANS = {"Released by Customs", "Arrival at Delivery Depot", "Arrival at Hub", "Out for Delivery"}

# Define delivered statuses
DELIVERED_VARIANTS = {
    "Delivered", "Driver release - Delivered to a safe place",
    "Delivered to postbox", "Delivered to greenhouse",
    "Delivered to outbuilding", "Shipment delivered. Possible damage"
}

# Define action-required statuses
ACTION_REQUIRED_STATUSES = {
    "Held in Customs", "Awaiting Release from Customs",
    "Customs Clearance in Progress", "Held Awaiting Tax Payment by Receiver",
    "Address Issue - Additional Information Required",
    "Delivery Attempted - Address Problem", "Package on Hold for Delivery"
}

def get_final_status(ai_story, status_elements, scan_groups_list, resolving_scans):
    """Use OpenAI to determine the correct status based on AI story."""
    prompt = f"""
    You are a logistics expert. Analyze the shipping journey and return ONLY the most appropriate final status from the following list:
    {json.dumps(status_elements, indent=2)}

    **Rules:**
    - Choose ONLY one status from the list above. Do NOT generate any explanation or extra text.
    - Resolving scans indicate issue resolution.
    - If a new action-required scan appears, update accordingly.
    - Do NOT assume 'Delivered' if later scans suggest otherwise.
    - A Resolving scan from the list indicates issue resolution; no resolving scan means the status is still active.

    **Action-Required Scans:**
    {json.dumps(scan_groups_list, indent=2)}

    **Resolving Scans:**
    {json.dumps(resolving_scans, indent=2)}

    AI Story:
    {ai_story}

    Your response must contain ONLY one of the status elements from the list above.
    Example Output:
    Delivered
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"❌ Error processing story: {ai_story}")
        logging.error(f"Exception: {str(e)}")
        return "Error: AI Processing Failed"

def prepare_training_data(input_csv, output_jsonl, status_elements_file, scan_groups_file, resolving_scans_file):
    """Prepare training data with AI-powered assessment."""
    logging.info(f"📥 Loading training data: {input_csv}")
    df = pd.read_csv(input_csv)
    status_elements = load_json(status_elements_file)
    scan_groups_list = load_json(scan_groups_file)
    resolving_scans = load_json(resolving_scans_file)
    
    processed_count = 0
    skipped_count = 0
    
    with open(output_jsonl, "w") as f:
        for _, row in df.iterrows():
            ai_story = str(row["AiStory"]).strip()
            if not ai_story:
                skipped_count += 1
                continue

            correct_status = get_final_status(ai_story, status_elements, scan_groups_list, resolving_scans)
            if "Error" in correct_status:
                skipped_count += 1
                continue

            entry = {"messages": [
                {"role": "user", "content": ai_story},
                {"role": "assistant", "content": correct_status}
            ]}
            f.write(json.dumps(entry) + "\n")
            processed_count += 1
    
    logging.info(f"✅ Training data formatted and saved to {output_jsonl}")
    logging.info(f"📊 Summary: {processed_count} entries processed, {skipped_count} skipped")

def main():
    train_csv = "data/train.csv"
    training_jsonl = "data/training_data.jsonl"
    status_elements_file = "data/status_elements.json"
    scan_groups_file = "data/scan_groups.json"
    resolving_scans_file = "data/resolving_scans.json"

    logging.info("🚀 Starting JSONL Preparation...")
    prepare_training_data(train_csv, training_jsonl, status_elements_file, scan_groups_file, resolving_scans_file)
    logging.info("🎯 JSONL Preparation Completed!")

if __name__ == "__main__":
    main()
