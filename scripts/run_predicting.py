import sys
import os

# ✅ Ensure Python finds the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.logging_utils import logger  # ✅ Import centralized logger
from modules.user_input import get_model_type, get_model_name, get_api_key, select_csv_column  
from modules.file_handler import get_output_file, open_file_after_save  # ✅ Now correctly importing get_output_file
from modules.prediction_processor import process_csv
from config.settings_loader import SETTINGS  # ✅ Ensure settings are loaded first

# Log script start
logger.info("🚀 Starting AI prediction process...")

# Get user configurations
get_model_type()
get_model_name()
get_api_key()

# Get file paths
input_file = input("📂 Enter path to input CSV file: ").strip()
output_file = get_output_file()  # ✅ Now correctly generating output file path

if not os.path.exists(input_file):
    logger.error(f"❌ Input file '{input_file}' not found. Exiting.")
    exit(1)

# ✅ Select the CSV column dynamically
selected_column = select_csv_column(input_file)

# ✅ Ask user for the JSON prompt file
prompt_file = input("📂 Enter the name of the JSON prompt file to use (from data/prompts/): ").strip()

# ✅ Ensure only the filename is passed (Fix for double path issue)
prompt_file = os.path.basename(prompt_file)

# ✅ Validate prompt file path
prompt_path = os.path.join("data/prompts/", prompt_file)

if not os.path.exists(prompt_path):
    logger.error(f"❌ Prompt file '{prompt_path}' not found. Exiting.")
    exit(1)

# Run AI predictions
logger.info(f"📂 Processing file: {input_file} with prompt {prompt_file}")
process_csv(input_file, output_file, selected_column, prompt_file)  # ✅ Pass selected column & prompt file
logger.info("✅ AI prediction process completed!")

# ✅ Ensure file exists before trying to open it
if os.path.exists(output_file):
    open_file_after_save(output_file)
else:
    logger.warning("⚠️ No predictions were made, output file was not created.")