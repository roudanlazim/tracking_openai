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

logger.info("🚀 Starting AI prediction process...")

# ✅ Step 1: Get Model Type (e.g., OpenAI)
get_model_type()

# ✅ Step 2: Get Model Name (e.g., GPT-4)
get_model_name()

# ✅ Step 3: Get API Key
get_api_key()

# ✅ Step 4: CSV Selection
select_csv_file()

# ✅ Step 5: Column Selection
select_csv_column()

# ✅ Step 6: JSON Prompt Selection
select_prompt()

# ✅ Step 7: Confirmation Before Execution
if not confirm_selection():
    logger.info("🚫 Process canceled by user.")
    print("\n🚫 Process canceled. No API calls were made.")
    exit(0)

# ✅ Step 8: Process CSV with AI Model
output_file = get_output_file()
logger.info(f"🚀 Processing file: {SystemSettings.input_file} using model {SystemSettings.model_name} and prompt {SystemSettings.prompt_file}")

process_csv(SystemSettings.input_file, output_file, SystemSettings.selected_column, SystemSettings.prompt_file)

# ✅ Step 9: Save results & Open CSV automatically
logger.info("✅ AI prediction process completed!")

if os.path.exists(output_file):
    open_file_after_save(output_file)
else:
    logger.warning("⚠️ No predictions were made, output file was not created.")