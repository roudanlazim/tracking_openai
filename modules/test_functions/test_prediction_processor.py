import sys
import os
import getpass  # ✅ Hide API key input
import pandas as pd

# ✅ Add project root to `sys.path` so Python can find `modules/`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from modules.prediction_processor import process_row, process_csv
from modules.file_handler import save_csv, load_csv
from modules.system_settings import SystemSettings
from modules.prompt_generator import load_prompt
from modules.logging_utils import logger  # ✅ Import centralized logger

# ✅ Step 1: Ask for API Key (Hidden Input) & Store It
if not SystemSettings.api_key:
    SystemSettings.api_key = getpass.getpass("\n🔑 Enter your OpenAI API Key: ").strip()

if not SystemSettings.api_key:
    print("❌ No API Key entered. Exiting test.")
    sys.exit(1)

print(f"✅ API Key Stored: {SystemSettings.api_key[:6]}********")  # ✅ Masked API key

# ✅ Step 2: Define Paths & Ensure Prompt File Exists
TEST_DIR = os.path.abspath("data/test/")
os.makedirs(TEST_DIR, exist_ok=True)  # ✅ Ensure test directory exists

TEST_CSV_FILE = os.path.join(TEST_DIR, "test_predictions.csv")
TEST_PROMPT_FILE = os.path.abspath("data/prompts/example_prompt.json")  # ✅ Use absolute path

# ✅ Debugging: Print the absolute path to confirm location
print(f"🔍 Checking prompt file at: {TEST_PROMPT_FILE}")

if not os.path.exists(TEST_PROMPT_FILE):
    print(f"❌ Prompt file not found: {TEST_PROMPT_FILE}")
    sys.exit(1)

print(f"✅ Loaded Prompt from {TEST_PROMPT_FILE}")

# ✅ Load status elements for testing
TEST_STATUS_ELEMENTS = ["In Transit", "Delivered", "Exception"]

# ✅ STEP 1: CREATE TEST CSV FILE
print("\n📄 Creating test CSV file...")
test_data = pd.DataFrame([
    {"ScanGroups": "(2024-09-26T07:05:00) Delivery attempted, (2024-09-12T04:46:00) Delivery attempted, (2024-09-11T22:39:00) Arrival at delivery depot"},
    {"ScanGroups": "(2024-09-06T08:44:00) In Transit, (2024-09-05T08:31:00) Arrival scan, (2024-09-05T07:19:00) Export Scan"},
    {"ScanGroups": "(2024-09-05T03:20:00) Warehouse Scan, (2024-09-05T01:12:00) Warehouse Scan, (2024-09-05T01:00:00) In Transit"}
])
save_csv(test_data, TEST_CSV_FILE)
print(f"✅ Test CSV File Created: {TEST_CSV_FILE}")

### ✅ STEP 2: PROCESS A SINGLE ROW WITH MULTIPLE SCANS
print("\n📄 Testing process_row()")

sample_input = "(2024-09-26T07:05:00) Delivery attempted, (2024-09-12T04:46:00) Delivery attempted, (2024-09-11T22:39:00) Arrival at delivery depot"
structured_prompt = load_prompt(TEST_PROMPT_FILE)  # ✅ Load JSON prompt structure
prediction_result = process_row(sample_input, TEST_PROMPT_FILE)

print(f"✅ Processed Row Prediction: {prediction_result}")

### ✅ STEP 3: PROCESS ENTIRE CSV FILE
print("\n📄 Testing process_csv()")
SystemSettings.input_file = TEST_CSV_FILE  # ✅ Ensure input file is set
SystemSettings.selected_column = "ScanGroups"  # ✅ Use `ScanGroups` column for shipment tracking
output_file = os.path.join(TEST_DIR, "test_predictions_output.csv")

process_csv(TEST_CSV_FILE, output_file, "ScanGroups", TEST_PROMPT_FILE)

print(f"✅ Predictions saved to: {output_file}")

# ✅ Load and Print Results
df_results = load_csv(output_file)
print("\n📊 Prediction Results Preview:")
print(df_results.head())  # ✅ Show first few rows

# ✅ Load and Print Results
df_results = load_csv(output_file)
print("\n📊 Prediction Results Preview:")
print(df_results.head())  # ✅ Show first few rows