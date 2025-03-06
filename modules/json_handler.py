import json
import os
from datetime import datetime
from modules.logging_utils import logger

# ✅ Ensure `data/` and `config/` directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("config", exist_ok=True)

def find_json_file(filename):
    """Search for a JSON file dynamically in `data/`, `config/`, or anywhere in the project."""
    search_dirs = ["data", "config"]  # ✅ Prioritize these directories

    # ✅ First, check `data/` and `config/`
    for directory in search_dirs:
        potential_path = os.path.join(directory, filename)
        if os.path.exists(potential_path):
            return potential_path

    # ✅ If not found, search the entire project directory
    for root, _, files in os.walk(os.getcwd()):
        if filename in files:
            found_path = os.path.join(root, filename)
            print(f"\n🟢 DEBUG: Found JSON file in `{found_path}` (Project-wide search)")
            return found_path

    print(f"\n❌ DEBUG: JSON file `{filename}` not found in `data/`, `config/`, or anywhere in the project!")
    return None

def list_json_files(directory="data"):
    """List all available JSON files in a given directory or search entire project if not found."""
    json_files = []

    # ✅ Check specified directory first
    dir_path = os.path.abspath(directory)
    if os.path.exists(dir_path):
        json_files.extend([f for f in os.listdir(dir_path) if f.endswith(".json")])

    # ✅ If no JSON files were found, search the entire project
    if not json_files:
        for root, _, files in os.walk(os.getcwd()):
            for file in files:
                if file.endswith(".json"):
                    json_files.append(os.path.join(root, file))

    if not json_files:
        print("\n❌ DEBUG: No JSON files found in `data/`, `config/`, or anywhere in the project!")
    else:
        print("\n📂 Available JSON Files:")
        for idx, file in enumerate(json_files, start=1):
            print(f"{idx} - {file}")

    return json_files

def load_json(filename, fallback=None):
    """Load a JSON file dynamically, searching in `data/`, `config/`, or the entire project."""
    json_path = find_json_file(filename)  # ✅ Locate the JSON file

    if json_path is None:
        print(f"\n❌ DEBUG: JSON file `{filename}` not found. Using fallback data.")  # ✅ Debug print
        logger.error(f"❌ Error: JSON file `{filename}` not found!")
        return fallback

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        logger.info(f"✅ Loaded JSON file: {json_path}")
        return data
    except Exception as e:
        print(f"\n❌ DEBUG: Failed to load JSON file `{json_path}`. Error: {e}")  # ✅ Debug print
        logger.error(f"❌ Error loading JSON file {json_path}: {str(e)}")
        return fallback
    
import json
import os
from modules.logging_utils import logger

def save_json(data, filename="predictions.json"):
    """Append new data to an existing JSON file instead of overwriting it."""
    os.makedirs("output", exist_ok=True)
    json_path = os.path.join("output", filename)

    try:
        # ✅ If file exists, load existing data and append new data
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        existing_data.extend(data)  # ✅ Append new data

        # ✅ Save the updated list back to JSON
        with open(json_path, "w") as f:
            json.dump(existing_data, f, indent=4)

        logger.info(f"✅ Updated JSON file: {json_path}")
        return json_path

    except Exception as e:
        logger.error(f"❌ Error saving JSON file {json_path}: {e}")
        return None
