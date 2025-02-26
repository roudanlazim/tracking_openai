import openai
import pandas as pd
import json
import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

# ✅ Load Environment Variables
load_dotenv()

# ✅ Configure Logging
logging.basicConfig(
    level=logging.DEBUG,  # Enable detailed debugging logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Log to console
)

# ✅ Use OpenAI client authentication
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("❌ ERROR: OPENAI_API_KEY not found in environment variables.")
    raise ValueError("❌ ERROR: OPENAI_API_KEY not found in environment variables.")

client = openai.OpenAI(api_key=api_key)
logging.info(f"🔹 Using API Key: {api_key[:10]}********")  # Mask API Key for security

# ✅ Set the fine-tuned model ID
FINE_TUNED_MODEL = "ft:gpt-3.5-turbo-0125:personal::AwC25u9x"  # Replace with your model ID

# ✅ API Rate Limits
API_CALLS_PER_MIN = 50  # Adjust based on OpenAI quota
SLEEP_TIME = 60 / API_CALLS_PER_MIN  # Pause to prevent hitting API rate limit

def get_final_status(ai_story):
    """Send request to OpenAI fine-tuned model to determine final status."""
    prompt = f"""
    Analyze the following shipment tracking history and return the most accurate final status.

    **AI Story:**
    {ai_story}

    Return ONLY the final shipment status as a single phrase. No extra text.
    """

    logging.debug("Sending request to OpenAI API...")

    try:
        response = client.chat.completions.create(
            model=FINE_TUNED_MODEL,  # ✅ Use fine-tuned model
            messages=[{"role": "system", "content": "You are an expert in shipment tracking status classification."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )

        predicted_status = response.choices[0].message.content.strip()

        # ✅ Capture Token Usage
        token_input = response.usage.prompt_tokens
        token_output = response.usage.completion_tokens

        logging.debug(f"AI Response: {predicted_status}")
        logging.debug(f"Tokens Used - Input: {token_input}, Output: {token_output}")

        return predicted_status, token_input, token_output

    except Exception as e:
        logging.error(f"❌ Error processing AI story: {ai_story}")
        logging.error(f"Exception: {str(e)}")
        return f"Error: {str(e)}", 0, 0

def process_csv(input_file, output_file):
    """Process CSV file and use fine-tuned model to predict statuses."""
    logging.info(f"📥 Loading input CSV: {input_file}")
    df = pd.read_csv(input_file)

    # ✅ Store results
    results = []
    logging.info("🚀 Processing AI stories...")

    for index, row in df.iterrows():
        logging.debug(f"🔎 Processing row {index+1}...")

        predicted_status, token_input, token_output = get_final_status(row["ai_story"])
        time.sleep(SLEEP_TIME)  # ✅ Prevent hitting OpenAI API rate limits

        # ✅ Handle missing expected status gracefully
        expected_status = str(row.get("expected_status", "")).strip().lower() if pd.notna(row.get("expected_status")) else "N/A"
        predicted_status = predicted_status.strip().lower()

        # ✅ Compare predicted vs expected status
        match_status = "N/A" if expected_status == "N/A" else ("1" if predicted_status == expected_status else "0")

        results.append({
            "ai_story": row["ai_story"],
            "expected_status": expected_status,
            "Predicted_Status": predicted_status,
            "Token_Input": token_input,
            "Token_Output": token_output,
            "Match_Status": match_status  # "N/A" if no expected status provided
        })

    # ✅ Convert results to DataFrame & save
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_file, index=False)

    logging.info(f"✅ Testing completed! Results saved in {output_file}")

if __name__ == "__main__":
    # ✅ File paths
    input_csv = "data/ai_stories.csv"
    output_csv = f"data/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    logging.info("🚀 Starting AI Status Testing Process...")
    
    # ✅ Process the CSV using the fine-tuned model
    process_csv(input_csv, output_csv)

    logging.info("🎯 AI Status Testing Completed Successfully!")
