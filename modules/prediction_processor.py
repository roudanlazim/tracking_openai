from modules.logging_utils import logger
from modules.file_handler import load_csv, save_csv
from modules.json_handler import save_json
from modules.prompt_generator import generate_prompt
from modules.ai_model import get_openai_response
from modules.conversation_handler import ConversationHandler
import pandas as pd  # ✅ Ensure Pandas is imported for NaN checks

def process_csv(input_file, output_file, json_output_file, selected_column, prompt_file, max_tokens=8192):
    """Processes a CSV file row by row, makes predictions using AI, and saves results dynamically."""
    
    logger.info(f"📂 Loading input CSV: {input_file}")

    df = load_csv(input_file)
    if df is None:
        logger.error("❌ Failed to load CSV. Exiting.")
        return []

    # ✅ Initialize conversation with the system prompt
    conversation = ConversationHandler(prompt_file, max_token_limit=max_tokens)
    
    predictions = []
    batch_size = 50  # ✅ Save results every 50 rows to avoid memory overload

    for idx, row in df.iterrows():
        scan_history = row[selected_column]

        # ✅ Ensure scan_history is always a string (fixes TypeError issue)
        if pd.isna(scan_history):  # ✅ Handle NaN (empty values)
            scan_history = ""
        else:
            scan_history = str(scan_history).strip()  # ✅ Convert to string and remove leading/trailing spaces

        # ✅ Ensure timestamps are explicitly included
        if scan_history:
            scan_history = "Scan History:\n" + scan_history  # ✅ Makes sure GPT recognizes it

        # ✅ Reset conversation if token limit is exceeded
        if conversation.token_count + conversation.count_tokens(scan_history) > max_tokens:
            logger.info("⚠️ Token limit exceeded, resetting conversation state.")
            conversation.reset_conversation()

        # ✅ Generate structured AI prompt
        prompt_messages = generate_prompt(scan_history, prompt_file)
        
        # ✅ Skip if prompt generation fails
        if not prompt_messages:
            continue

        # ✅ Query GPT for prediction
        predicted_status, token_input, token_output = get_openai_response(prompt_messages)

        # ✅ Add response to conversation history
        conversation.add_to_history("user", scan_history)
        conversation.add_to_history("assistant", predicted_status)

        # ✅ Store the result in memory
        predictions.append({
            "Input_Text": scan_history,
            "Predicted_Status": predicted_status,
            "Token_Input": token_input,
            "Token_Output": token_output
        })

        # ✅ Save periodically to avoid memory overload
        if idx % batch_size == 0:
            save_json(predictions, json_output_file)  # ✅ Saves intermediate results
            save_csv(df, output_file)  # ✅ Save to CSV dynamically
            logger.info(f"✅ Intermediate results saved. Processed {idx + 1} rows so far.")

    # ✅ Final Save after processing all rows
    save_json(predictions, json_output_file)
    save_csv(df, output_file)

    logger.info("✅ Processing complete. All predictions saved.")
    return predictions