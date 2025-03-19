import json
import os
from datetime import datetime
from modules.logging_utils import logger

# Ensure directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("config", exist_ok=True)

def find_json_file(filename):
    """Find a JSON file by name."""
    # Check 'data' and 'config' directories first
    for directory in ["data", "config"]:
        potential_path = os.path.join(directory, filename)
        if os.path.exists(potential_path):
            logger.info(f"✅ Found JSON file: {potential_path}")
            return potential_path

    # Search entire project if not found
    for root, _, files in os.walk(os.getcwd()):
        if filename in files:
            found_path = os.path.join(root, filename)
            logger.info(f"✅ Found JSON file at {found_path}")
            return found_path

    logger.error(f"❌ JSON file `{filename}` not found.")
    return None

def list_json_files(directory="data"):
    """List JSON files in specified directory or entire project."""
    json_files = []
    dir_path = os.path.abspath(directory)

    if os.path.exists(dir_path := dir_path):
        json_files = [f for f in os.listdir(dir_path) if f.endswith(".json")]
    else:
        for root, _, files in os.walk(os.getcwd()):
            json_files.extend([os.path.join(root, f) for f in files if f.endswith(".json")])

    if json_files:
        logger.info("📂 JSON Files found:")
        for file in json_files:
            logger.info(file)
    else:
        logger.warning("❌ No JSON files found anywhere.")

    return json_files

def load_json(filename):
    """Load a JSON file safely."""
    if not os.path.exists(filename):
        print(f"🚨 File Not Found: {filename}")
        return None

    try:
        with open(filename, "r", encoding="utf-8") as file:  # Ensure UTF-8 encoding
            data = json.load(file)
            print(f"✅ JSON Loaded Successfully from {filename}")
            return data
    except Exception as e:
        print(f"❌ JSON Load Error: {e}")
        return None

def save_json(data, filename=None, directory="output"):
    """Save data to JSON, uniquely named by timestamp."""
    os.makedirs(directory := "data", exist_ok=True)

    # Default filename with timestamp to prevent overwrites
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = filename or f"response_{timestamp}.json"
    file_path = os.path.join("data", filename)

    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=2)
            logger.info(f"✅ JSON response saved at `{file_path}`.")
        return file_path
    except Exception as e:
        logger.error(f"❌ Error saving JSON file `{file_path}`: {e}")
        return None

def append_json(data, filename="predictions.json"):
    """Append data to existing JSON file (expects list data)."""
    os.makedirs(directory := "output", exist_ok=True)
    file_path = os.path.join(directory, filename)

    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                existing_data = json.load(file)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
        else:
            existing_data = []

        existing_data.extend(data if isinstance(data, list) else [data])

        with open(file_path, "w") as file:
            json.dump(existing_data, file, indent=2)
            logger.info(f"✅ Data appended to `{file_path}`.")
    except Exception as e:
        logger.error(f"❌ Error appending to JSON `{file_path}`: {e}")