from modules.logging_utils import logger
import pandas as pd
from modules.file_handler import load_csv, save_csv
from modules.ai_model import get_ai_prediction
from modules.system_settings import SystemSettings
from modules.prompt_generator import generate_prompt, load_prompt  # ✅ Correct imports

def process_row(scan_history, prompt_file):
    """Process a single row and get AI prediction using full shipment history."""
    try:
        scan_history = str(scan_history).strip()

        if not scan_history:
            logger.warning("⚠️ Skipping empty input row.")
            return {
                "Input_Text": "EMPTY",
                "Predicted_Status": "Error",
                "Token_Input": 0,
                "Token_Output": 0
            }

        # ✅ Ensure `status_elements` is loaded before using it
        if not SystemSettings.status_elements:
            SystemSettings.load_status_elements()

        # ✅ Generate the AI Prompt using full `ScanGroups`
        structured_prompt = generate_prompt(prompt_file, scan_history, SystemSettings.status_elements)

        # ✅ Print and Log Full AI Request for Debugging
        print("\n🔍 **AI REQUEST (Prompt Sent to OpenAI):**")
        print(structured_prompt)
        logger.info(f"📨 AI Input:\n{structured_prompt}")

        # ✅ Call AI Model
        predicted_status, token_input, token_output = get_ai_prediction(
            structured_prompt, SystemSettings.status_elements, prompt_file
        )

        return {
            "Input_Text": scan_history,
            "Predicted_Status": predicted_status,
            "Token_Input": token_input,
            "Token_Output": token_output
        }
    
    except Exception as e:
        logger.error(f"❌ Error processing row: {str(e)}")
        return {
            "Input_Text": scan_history,
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

    # ✅ **Ensure `status_elements.json` is loaded before processing**
    if not SystemSettings.status_elements:
        SystemSettings.load_status_elements()

    logger.info(f"🚀 Processing predictions for column '{selected_column}' using prompt '{prompt_file}'...")

    results = []
    for _, row in df.iterrows():
        input_text = row[selected_column]  # ✅ Extract `ScanGroups` for prediction
        results.append(process_row(input_text, prompt_file))

    # ✅ Convert results list to DataFrame before saving
    results_df = pd.DataFrame(results)
    save_csv(results_df, output_file)
    logger.info(f"✅ Predictions saved to: {output_file}")
