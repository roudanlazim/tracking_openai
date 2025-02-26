from modules.logging_utils import logger
import pandas as pd
from modules.file_handler import load_csv, save_csv  # ✅ Correct function import
from modules.ai_model import get_openai_response
from modules.prompt_generator import generate_prompt
from config.settings_loader import CACHED_JSON_DATA  # ✅ Use cached JSON from settings_loader

def process_row(input_text, status_elements, prompt_file):
    """Process a single row for AI prediction."""
    try:
        input_text = str(input_text).strip()
        prompt = generate_prompt(input_text, status_elements, prompt_file)  # ✅ Uses dynamic prompt file
        predicted_status, token_input, token_output = get_openai_response(prompt)

        return {
            "Input_Text": input_text,
            "Predicted_Status": predicted_status,
            "Token_Input": token_input,
            "Token_Output": token_output
        }
    
    except Exception as e:
        logger.error(f"❌ Error processing row: {str(e)}")
        return {
            "Input_Text": input_text,
            "Predicted_Status": "Error",
            "Token_Input": 0,
            "Token_Output": 0
        }

def process_csv(input_file, output_file, selected_column, prompt_file):
    """Process an entire CSV file and run AI predictions."""
    logger.info(f"📂 Loading input CSV: {input_file}")

    df = load_csv(input_file)
    if df is None:
        logger.error("❌ Failed to load CSV. Exiting.")
        return

    if selected_column not in df.columns:
        logger.error(f"❌ Column '{selected_column}' not found in CSV. Available columns: {list(df.columns)}")
        return  

    status_elements = CACHED_JSON_DATA.get("status_elements", {"statuses": ["Delivered", "In Transit", "Returned to Sender"]})  # ✅ Ensure default values exist

    results = []
    logger.info(f"🚀 Processing predictions for column '{selected_column}' using prompt '{prompt_file}'...")

    for _, row in df.iterrows():
        results.append(process_row(row[selected_column], status_elements, prompt_file))

    # Convert results list to DataFrame before saving
    results_df = pd.DataFrame(results)
    save_csv(results_df, output_file)  # ✅ Now correctly calling save_csv()