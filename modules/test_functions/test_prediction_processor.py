import sys
import os
import pandas as pd
import json

# ✅ Add project root to `sys.path` so Python can find `modules/`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from modules.prediction_processor import process_row, process_csv
from modules.file_handler import save_csv, load_csv
from modules.system_settings import SystemSettings

# ✅ Test Directory and Files
TEST_DIR = "data/test/"
os.makedirs(TEST_DIR, exist_ok=True)  # Ensure test directory exists
TEST_CSV_FILE = os.path.join(TEST_DIR, "test_predictions.csv")
TEST_PROMPT_FILE = "data/prompts/example_prompt.json"  # ✅ Ensure prompt exists

# ✅ Load status elements for testing
TEST_STATUS_ELEMENTS = ["In Transit", "Delivered", "Exception"]

### ✅ STEP 1: CREATE TEST CSV FILE
print("\n📄 Creating test CSV file...")
test_data = pd.DataFrame([
    {"Tracking_Info": "Package scanned at facility"},
    {"Tracking_Info": "Package delivered to customer"},
    {"Tracking_Info": "Delivery attempt failed"}
])
save_csv(test_data, TEST_CSV_FILE)
print(f"✅ Test CSV File Created: {TEST_CSV_FILE}")

### ✅ STEP 2: PROCESS A SINGLE ROW
print("\n📄 Testing process_row()")
sample_input = "Package scanned at facility"
prediction_result = process_row(sample_input, TEST_STATUS_ELEMENTS, TEST_PROMPT_FILE)
print(f"✅ Processed Row Prediction: {prediction_result}")

### ✅ STEP 3: PROCESS ENTIRE CSV FILE
print("\n📄 Testing process_csv()")
SystemSettings.input_file = TEST_CSV_FILE  # ✅ Ensure input file is set
SystemSettings.selected_column = "Tracking_Info"  # ✅ Use the correct column
output_file = os.path.join(TEST_DIR, "test_predictions_output.csv")

process_csv(TEST_CSV_FILE, output_file, "Tracking_Info", TEST_PROMPT_FILE)
print(f"✅ Predictions saved to: {output_file}")

### ✅ S