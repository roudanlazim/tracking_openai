import sys
import os

# ✅ Dynamically add project root to `sys.path`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# ✅ Now import modules
from modules.json_handler import format_prediction, save_json, load_json
from modules.system_settings import SystemSettings
from modules.logging_utils import logger

# ✅ Ensure test directory exists
TEST_DIR = os.path.abspath("data/test/")
os.makedirs(TEST_DIR, exist_ok=True)

# ✅ Set a test model name for SystemSettings
SystemSettings.model_name = "gpt-3.5-turbo"

# ✅ Define Test JSON File
TEST_JSON_FILE = os.path.join(TEST_DIR, "test_predictions.json")

logger.info(f"Starting JSON Handler Test... Saving to {TEST_JSON_FILE}")

# ✅ Test Data
test_predictions = [
    format_prediction("SHIP123", "Package scanned at facility.", "In Transit", 50, 10),
    format_prediction("SHIP456", "Out for delivery.", "Out for Delivery", 45, 12)
]

# ✅ Step 1: Save JSON incrementally
json_path = save_json(test_predictions, "test_predictions", incremental_save=True)

# ✅ Step 2: Load JSON and verify
if json_path and os.path.exists(json_path):
    loaded_data = load_json(os.path.basename(json_path))
    print("\nLoaded Test JSON Data:")
    print(loaded_data)

    # ✅ Step 3: Verify data consistency
    assert len(loaded_data) >= len(test_predictions), "Data loss detected!"
    print("\n✅ JSON Handler Test Passed Successfully!")

else:
    print("\n❌ JSON file was not saved properly. Check logs for errors.")