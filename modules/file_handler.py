import os
import json
import pandas as pd
import platform
import subprocess
from pathlib import Path
from modules.logging_utils import logger  # ✅ Import centralized logger

# ✅ Ensure `data/` directory is dynamically detected
def find_data_dir():
    """Dynamically locate the `data/` directory from any script location."""
    current_dir = os.path.dirname(os.path.abspath(__file__))  # ✅ Get current script directory

    while current_dir:
        potential_data_dir = os.path.join(current_dir, "data")
        if os.path.exists(potential_data_dir):
            return potential_data_dir  # ✅ Return the first valid `data/` directory found

        # ✅ Move up one directory
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # ✅ Stop at root directory
            break
        current_dir = parent_dir

    raise FileNotFoundError("❌ ERROR: `data/` directory not found!")  # ✅ Stop execution if `data/` is missing

# ✅ Define core directories dynamically
DATA_DIR = find_data_dir()
PROMPT_DIR = os.path.join(DATA_DIR, "prompts")
OUTPUT_DIR = "output/"  # ✅ Ensures predictions are saved in `output/`

# ✅ Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PROMPT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_csv(csv_path):
    """Load a CSV file into a DataFrame, ensuring the correct file is used."""
    try:
        # ✅ Convert relative paths to absolute paths
        if not os.path.isabs(csv_path):
            csv_path = os.path.join(DATA_DIR, os.path.basename(csv_path))

        logger.info(f"🟢 Attempting to load CSV file: `{csv_path}`...")

        if not os.path.exists(csv_path):
            logger.error(f"❌ CSV file `{csv_path}` does not exist!")
            return None
        
        df = pd.read_csv(csv_path)
        logger.info(f"✅ Successfully loaded CSV file `{csv_path}`.")
        return df
    except Exception as e:
        logger.error(f"❌ Error loading CSV file `{csv_path}`: {str(e)}")
        return None

def get_model_name():
    """Retrieve the model name dynamically to avoid circular import issues."""
    from modules.system_settings import SystemSettings  # ✅ Lazy import to avoid circular import issues
    return SystemSettings.model_name if SystemSettings.model_name else "gpt-3.5-turbo"

def get_output_file():
    """Return the full path for the output CSV file."""
    output_file = os.path.join(OUTPUT_DIR, "predictions.csv")
    logger.info(f"✅ Output file set to: {output_file}")
    return output_file

def save_csv(df, filename="predictions.csv"):
    """Save AI predictions to CSV in `output/`, including token usage and estimated cost. Updates existing file if available."""
    
    if df is None or df.empty:
        logger.warning("⚠️ No predictions to save. Skipping CSV save.")
        return

    # ✅ Full path to CSV file in `output/`
    csv_path = os.path.join(OUTPUT_DIR, filename)

    # ✅ Define OpenAI token pricing dynamically
    pricing_table = {
        "gpt-3.5-turbo": {"input_cost": 0.001, "output_cost": 0.002},
        "gpt-4": {"input_cost": 0.03, "output_cost": 0.06},
        "gpt-4-turbo": {"input_cost": 0.01, "output_cost": 0.03},
        "gpt-4o": {"input_cost": 0.03, "output_cost": 0.06},
    }

    from modules.system_settings import SystemSettings  # ✅ Lazy import to prevent circular import issues
    model = SystemSettings.model_name if SystemSettings.model_name else "gpt-3.5-turbo"
    model_pricing = pricing_table.get(model, pricing_table["gpt-3.5-turbo"])

    # ✅ Ensure required columns exist
    for col in ["Token_Input", "Token_Output"]:
        if col not in df.columns:
            df[col] = 0

    # ✅ Compute total tokens and estimated cost
    df["Total_Tokens"] = df["Token_Input"] + df["Token_Output"]
    df["Estimated_Cost ($USD)"] = (df["Token_Input"] / 1000) * model_pricing["input_cost"] + \
                                  (df["Token_Output"] / 1000) * model_pricing["output_cost"]

    try:
        # ✅ Check if CSV file exists, load existing data and append
        if os.path.exists(csv_path):
            existing_df = pd.read_csv(csv_path)
            df = pd.concat([existing_df, df], ignore_index=True)

        # ✅ Save updated CSV in `output/`
        df.to_csv(csv_path, index=False)
        logger.info(f"✅ Updated predictions saved to CSV: {csv_path}")

    except Exception as e:
        logger.error(f"❌ Error saving CSV file `{csv_path}`: {str(e)}")

def open_file_after_save(csv_path):
    """Automatically open the CSV file after saving, ensuring Excel opens on Windows."""
    try:
        if platform.system() == "Windows":
            subprocess.run(["cmd.exe", "/c", "start", "", csv_path], shell=True)
            logger.info(f"✅ Opened file in Excel (Windows): {csv_path}")
        elif platform.system() == "Darwin":  # ✅ macOS
            os.system(f"open -a 'Microsoft Excel' {csv_path}")  
            logger.info(f"✅ Opened file in Excel (macOS): {csv_path}")
        else:  # ✅ Linux
            os.system(f"xdg-open {csv_path}")  
            logger.info(f"✅ Opened file in system default application (Linux): {csv_path}")
    except Exception as e:
        logger.error(f"⚠️ Could not open file: {str(e)}")

def list_files(subdirectory, extension):
    """List all files with a given extension inside `data/`."""
    try:
        directory = os.path.join(DATA_DIR, subdirectory)  # ✅ Always search inside `data/`
        absolute_path = os.path.abspath(directory)

        if not os.path.exists(directory):
            logger.warning(f"⚠️ Directory not found: {directory}")
            return []

        files = [f for f in os.listdir(directory) if f.endswith(extension)]
        logger.info(f"✅ Found {len(files)} '{extension}' files in {directory}.")
        return files
    except Exception as e:
        logger.error(f"❌ Error listing files in `{directory}`: {str(e)}")
        return []

def apply_proposed_sg_to_csv(mapping_csv_path, scan_groups_path, output_csv_path, proposed_matches, run_label=None, column_name=None):
    """
    Adds a uniquely named column (e.g. 'proposed_sg_20240402_1030') to the mapping CSV using AI-provided suggestions.

    Parameters:
    - mapping_csv_path: Full path to the scan group mapping CSV (source).
    - scan_groups_path: Full path to the known scan groups CSV (reference).
    - output_csv_path: Full path to save the updated CSV with a new `proposed_sg_*` column.
    - proposed_matches: List of dicts with {"original": scan_name, "proposed_sg": scan_group}
    - run_label: Optional string label for this column (e.g. "run1" or "gpt4o")
    """
    import pandas as pd
    import os
    from datetime import datetime
    from modules.logging_utils import logger

    try:
        # ✅ Load existing output file or fallback to original
        if os.path.exists(output_csv_path):
            df = pd.read_csv(output_csv_path)
            print(f"📄 Loaded existing output CSV: {output_csv_path}")
        else:
            df = pd.read_csv(mapping_csv_path)
            print(f"📄 Loaded original mapping CSV: {mapping_csv_path}")

        scan_groups = pd.read_csv(scan_groups_path)["scan_group"].tolist()
        proposed_dict = {match["original"]: match["proposed_sg"] for match in proposed_matches}

        # ✅ Generate a unique column name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        from modules.system_settings import SystemSettings  # Add near top if not already imported
        model = SystemSettings.model_name if SystemSettings.model_name else "gpt"
        col_name = f"proposed_sg_{model}_{run_label or timestamp}"
        counter = 1
        original_col_name = col_name
        while col_name in df.columns:
            col_name = f"{original_col_name}_{counter}"
            counter += 1

        # ✅ Generate values
        def get_proposed(scan_name):
            suggestion = proposed_dict.get(scan_name.strip(), None)
            if not suggestion:
                return ""
            if suggestion not in scan_groups and not suggestion.startswith(("not_clear", "unclear__")):
                return f"new__{suggestion}"
            return suggestion

        target_column = column_name if column_name and column_name in df.columns else "scan_name"
        df[col_name] = df[target_column].apply(get_proposed)

        # ✅ Save updated CSV
        df.to_csv(output_csv_path, index=False)
        logger.info(f"✅ Saved scan group alignment with column '{col_name}' to: {output_csv_path}")
        print(f"✅ Column '{col_name}' written to:\n{output_csv_path}")

        # ✅ Write alignment log
        log_filename = f"alignment_log_{run_label or timestamp}.csv"
        log_path = os.path.join(os.path.dirname(output_csv_path), log_filename)

        log_entries = []
        for scan_name in df[target_column]:
            proposed = df.at[df[df[target_column] == scan_name].index[0], col_name]
            log_entries.append({
                "scan_name": scan_name,
                "proposed_scan_group": proposed,
                "note": "new" if proposed.startswith("new__") else ("unclear" if "unclear__" in proposed else "")
            })

        pd.DataFrame(log_entries).to_csv(log_path, index=False)
        print(f"📝 Alignment log written to: {log_path}")

    except Exception as e:
        print(f"❌ Failed to apply proposed scan groups: {e}")