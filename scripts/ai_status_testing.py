import openai
import pandas as pd
import json
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Enable detailed debugging logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Log to console
)

# Use OpenAI client authentication
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("ERROR: OPENAI_API_KEY not found in environment variables.")
    raise ValueError("ERROR: OPENAI_API_KEY not found in environment variables.")

client = openai.OpenAI(api_key=api_key)
logging.info(f"Using API Key: {api_key[:10]}********")  # Mask API Key just so we can see what one is being used, sometimes the old key will remain in an environment. 

def load_json(file_path):
    """Load JSON data from a file."""
    logging.debug(f"Loading JSON file: {file_path}")
    with open(file_path, 'r') as file:
        return json.load(file)

def get_final_status(ai_story, status_elements, scan_groups_list, resolving_scans):
    """Send request to OpenAI API to determine the final status of a shipment and track token usage."""
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

    logging.debug("Sending request to OpenAI API...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )

        predicted_status = response.choices[0].message.content.strip()

        # Capture token usage
        token_input = response.usage.prompt_tokens
        token_output = response.usage.completion_tokens

        logging.debug(f"AI Response: {predicted_status}")
        logging.debug(f"Tokens Used - Input: {token_input}, Output: {token_output}")

        return predicted_status, token_input, token_output

    except Exception as e:
        logging.error(f"Error processing story: {ai_story}")
        logging.error(f"Exception: {str(e)}")
        return f"Error: {str(e)}", 0, 0

def process_csv(input_file, output_file, status_elements_file, scan_groups_file, resolving_scans_file):
    """Process CSV file to add AI-predicted statuses, token usage, and expected status match verification."""
    logging.info(f"Loading input CSV: {input_file}")
    df = pd.read_csv(input_file)

    # Load JSON files
    logging.info("📂 Loading status elements and scan rules...")
    status_elements = load_json(status_elements_file)
    scan_groups_list = load_json(scan_groups_file)
    resolving_scans = load_json(resolving_scans_file)

    # Apply AI predictions and store token data
    results = []
    logging.info("🚀 Processing AI stories...")

    for index, row in df.iterrows():
        logging.debug(f"🔎 Processing row {index+1}...")

        predicted_status, token_input, token_output = get_final_status(
            row["ai_story"], status_elements, scan_groups_list, resolving_scans
        )

        # Handle missing expected_status gracefully
        expected_status = str(row.get("expected_status", "")).strip().lower() if pd.notna(row.get("expected_status")) else "N/A"
        predicted_status = predicted_status.strip().lower()

        # If expected_status is missing, don't compare, just store predicted value
        match_status = "N/A" if expected_status == "N/A" else ("1" if predicted_status == expected_status else "0")

        results.append({
            "ai_story": row["ai_story"],
            "expected_status": expected_status,
            "Predicted_Status": predicted_status,
            "Token_Input": token_input,
            "Token_Output": token_output,
            "Match_Status": match_status  # "N/A" if no expected status
        })

    # Convert to DataFrame and save results
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_file, index=False)

    logging.info(f"Testing completed! Results saved in {output_file}")

if __name__ == "__main__":
    # File paths - absolute paths - change these 
    input_csv = r"C:\Users\Shaalan\Tracking project\tracking_project_v1\data\ai_stories.csv"
    output_csv = rf"C:\Users\Shaalan\Tracking project\tracking_project_v1\data\results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    status_elements_file = r"C:\Users\Shaalan\Tracking project\tracking_project_v1\data\status_elements.json"
    scan_groups_file = r"C:\Users\Shaalan\Tracking project\tracking_project_v1\data\scan_groups.json"
    resolving_scans_file = r"C:\Users\Shaalan\Tracking project\tracking_project_v1\data\resolving_scans.json"

    logging.info("Starting AI Status Testing Process...")
    
    # Process the CSV
    process_csv(input_csv, output_csv, status_elements_file, scan_groups_file, resolving_scans_file)

    logging.info("AI Status Testing Completed Successfully!")
