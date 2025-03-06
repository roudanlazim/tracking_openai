import sys
import os

# ✅ Ensure Python finds the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.logging_utils import logger
from modules.user_input import (
    get_model_type, get_model_name, get_api_key, 
    select_csv_file, select_csv_column, select_prompt, confirm_selection
)
from modules.system_settings import SystemSettings
from modules.prediction_processor import process_csv
from modules.file_handler import get_output_file, open_file_after_save
from modules.json_handler import save_json  # ✅ Correctly using json_handler

logger.info("🚀 Starting AI prediction process...")

# ✅ Step 1: Get Model Type (e.g., OpenAI)
get_model_type()

# ✅ Step 2: Get Model Name (e.g., GPT-4)
get_model_name()
print("\n🟢 DEBUG: Model selection completed. Calling `select_csv_file()`...")  # ✅ Debug message
logger.info("🟢 DEBUG: Model selection completed. Calling `select_csv_file()`...")  

# ✅ Step 3: Get API Key
get_api_key()

# ✅ Step 4: CSV Selection
print("\n🟢 DEBUG: Model selection completed. Calling `select_csv_file()`...")  # ✅ Debug message
logger.info("🟢 DEBUG: Model selection completed. Calling `select_csv_file()`...")  
select_csv_file()  # ✅ Only called once
print("\n🟢 DEBUG: Proceeding to column selection...")  # ✅ Debug print

# ✅ Step 5: Column Selection
select_csv_column()

# ✅ Step 6: JSON Prompt Selection
selected_prompt = select_prompt()
print(f"\n🟢 DEBUG: Using JSON prompt `{selected_prompt}`")

# ✅ Step 7: Confirmation Before Execution
if not confirm_selection():
    logger.info("🚫 Process canceled by user.")
    print("\n🚫 Process canceled. No API calls were made.")
    exit(0)

# ✅ Step 8: Process CSV with AI Model
output_file = get_output_file()
logger.info(f"🚀 Processing file: {SystemSettings.input_file} using model {SystemSettings.model_name} and prompt {SystemSettings.prompt_file}")
json_output_file = "output/predictions.json"

predictions = process_csv(
    SystemSettings.input_file,  # ✅ CSV file
    output_file,  # ✅ Output CSV file
    json_output_file,  # ✅ Missing JSON output file (FIXED)
    SystemSettings.selected_column,  # ✅ Selected column
    SystemSettings.prompt_file  # ✅ Prompt file
)

# ✅ Step 9: Save JSON Predictions
json_output = save_json(predictions)  # ✅ Save results in JSON
logger.info(f"📂 Predictions also saved in JSON format: {json_output}")

# ✅ Step 10: Save results & Open CSV automatically
logger.info("✅ AI prediction process completed!")

if os.path.exists(output_file):
    open_file_after_save(output_file)
else:
    logger.warning("⚠️ No predictions were made, output file was not created.")

# ✅ Step 11: Keep session open until user exits manually
while True:
    choice = input("\n💬 Continue session? (yes/no): ").strip().lower()
    if choice == "no":
        logger.info("🚫 User ended the session.")
        print("🚫 Session ended.")
        break
    elif choice == "yes":
        print("✅ Session continues... You can process more shipments manually.")
    else:
        print("❌ Invalid choice. Please enter 'yes' or 'no'.")