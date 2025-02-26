import os
import json
import pandas as pd
import platform
import webbrowser
import subprocess
from pathlib import Path
from modules.logging_utils import logger  # ✅ Import centralized logger

DATA_DIR = "data/"
PROMPT_DIR = os.path.join(DATA_DIR, "prompts")
OUTPUT_DIR = "output/"  # ✅ Ensure predictions are saved in a dedicated folder

# ✅ Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PROMPT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_output_file():
    """Generate a unique output file name in the output directory."""
    output_file = os.path.join(OUTPUT_DIR, "predictions.csv")
    logger.info(f"✅ Output file set to: {output_file}")
    return output_file

def get_json_path(filename):
    """Return the full path of a JSON file in the `data/` directory."""
    return os.path.join(DATA_DIR, filename)  # ✅ Ensure it uses `data/` as the base directory

def load_json(json_path, fallback=None):  # ✅ Added fallback argument
    """Load JSON file and return its contents."""
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        logger.info(f"✅ Loaded JSON file: {json_path}")
        return data
    except Exception as e:
        logger.error(f"❌ Error loading JSON file {json_path}: {str(e)}")
        return fallback  # ✅ Returns fallback if the file doesn't load

def save_json(json_path, data):
    """Save data to a JSON file."""
    try:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"✅ Saved JSON file: {json_path}")
    except Exception as e:
        logger.error(f"❌ Error saving JSON file {json_path}: {str(e)}")

def load_csv(csv_path):
    """Load a CSV file into a DataFrame."""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"✅ Loaded CSV file: {csv_path}")
        return df
    except Exception as e:
        logger.error(f"❌ Error loading CSV file {csv_path}: {str(e)}")
        return None

def save_csv(df, csv_path):  # ✅ Rename from save_results to save_csv
    """Save a DataFrame to CSV and auto-open it."""
    try:
        df.to_csv(csv_path, index=False)
        logger.info(f"✅ Saved CSV file: {csv_path}")
        open_file_after_save(csv_path)  # ✅ Automatically open after saving
    except Exception as e:
        logger.error(f"❌ Error saving CSV file {csv_path}: {str(e)}")

def open_file_after_save(csv_path):
    """Automatically open the CSV file after saving, ensuring Excel opens on Windows."""
    try:
        if platform.system() == "Windows":
            # ✅ Force Excel to open the file instead of relying on os.startfile
            subprocess.run(["cmd.exe", "/c", "start", "", csv_path], shell=True)
            logger.info(f"✅ Opened file in Excel (Windows): {csv_path}")
            return  # ✅ Prevents browser fallback

        elif platform.system() == "Darwin":  # ✅ macOS
            os.system(f"open -a 'Microsoft Excel' {csv_path}")  
            logger.info(f"✅ Opened file in Excel (macOS): {csv_path}")
            return  # ✅ Prevents browser fallback

        else:  # ✅ Linux
            os.system(f"xdg-open {csv_path}")  
            logger.info(f"✅ Opened file in system default application (Linux): {csv_path}")
            return  # ✅ Prevents browser fallback

    except Exception as e:
        logger.error(f"⚠️ Could not open file with system default app: {str(e)}")
    
    # ✅ Prevent browser fallback completely if the file exists
    if os.path.exists(csv_path):
        logger.warning(f"⚠️ Skipping browser fallback to prevent duplicate openings.")

def list_files(directory, extension):
    """List all files with a given extension in a directory."""
    try:
        if not os.path.exists(directory):
            logger.warning(f"⚠️ Directory not found: {directory}")
            return []

        files = [f for f in os.listdir(directory) if f.endswith(extension)]
        logger.info(f"✅ Found {len(files)} '{extension}' files in {directory}.")
        return files
    except Exception as e:
        logger.error(f"❌ Error listing files in {directory}: {str(e)}")
        return []
