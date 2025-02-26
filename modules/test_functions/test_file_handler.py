import sys
import os
import pandas as pd
import json

# ✅ Add project root to `sys.path` so Python can find `modules/`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from modules.file_handler import (
    load_json, save_json, load_csv, save_csv, list_files, open_file_after_save
)

# ✅ Test Directory and Files
TEST_DIR = "data/test/"
os.makedirs(TEST_DIR, exist_ok=True)  # Ensure test directory exists
TEST_JSON_FILE = os.path.join(TEST_DIR, "test_data.json")
TEST_CSV_FILE = os.path.join(TEST_DIR, "test_data.csv")

### ✅ TEST JSON FUNCTIONS
print("\n📄 Testing save_json()")
test_json_data = {
    "instruction": "Analyze shipment tracking data and return the most appropriate status.",
    "status_elements": ["In Transit", "Delivered", "Exception"],
    "examples": [
        {"input": "Package scanned at facility", "output": "In Transit"},
        {"input": "Package delivered to customer", "output": "Delivered"}
    ]
}
save_json(TEST_JSON_FILE, test_json_data)
print(f"✅ Saved JSON File: {TEST_JSON_FILE}")

print("\n📄 Testing load_json()")
loaded_json = load_json(TEST_JSON_FILE)
print(f"✅ Loaded JSON Data:\n{json.dumps(loaded_json, indent=2)}")

# ✅ Confirm data integrity
if loaded_json == test_json_data:
    print("✅ JSON file saved and loaded correctly!")
else:
    print("❌ JSON file content does NOT match expected data!")

### ✅ TEST CSV FUNCTIONS
print("\n📄 Testing save_csv()")
test_df = pd.DataFrame([{"Name": "Alice", "Age": 25}, {"Name": "Bob", "Age": 30}])
save_csv(test_df, TEST_CSV_FILE)

print("\n📄 Testing load_csv()")
loaded_csv = load_csv(TEST_CSV_FILE)
print(f"✅ Loaded CSV Data:\n{loaded_csv}")

### ✅ TEST LIST FILES FUNCTION
print("\n📄 Testing list_files()")
json_files = list_files(TEST_DIR, ".json")
csv_files = list_files(TEST_DIR, ".csv")
print(f"✅ Found JSON Files: {json_files}")
print(f"✅ Found CSV Files: {csv_files}")

### ✅ TEST OPEN FILE FUNCTION
print("\n📄 Testing open_file_after_save() (Only works if you have a default app for CSV)")
open_file_after_save(TEST_CSV_FILE)