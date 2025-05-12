import pandas as pd
import os
import re

# === PATH CONFIGURATION ===
CODES_FILE = r"C:\Users\Shaalan\tracking_openai\data\pvr_config_data\scan_codes.csv"
EXCEL_FILE = r"C:\Users\Shaalan\tracking_openai\data\pvr_config_data\unmatched_scans_to_map_1004_raw.csv"
SHEET_NAME = "unmatched_scans_to_map_1004_raw"
OUTPUT_FILE = EXCEL_FILE.replace(".csv", "_decoded.csv")

# === LOAD CODE MAPPINGS (with case-insensitive keys) ===
def load_code_map(path):
    try:
        df = pd.read_csv(path).applymap(str)
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="ISO-8859-1").applymap(str)

    return {
        str(row['code']).strip().lower(): str(row['scan']).strip()
        for _, row in df.iterrows()
    }

# === SKIP LIST: Known descriptive single words (not codes) ===
skip_values = {
    "delivery", "damaged", "recogido", "transit", "lost", "money", "carded",
    "top", "bottom", "button", "leg", "door", "none", "bell", "deadline", "deadlines",
    "stopped", "missort", "liquid", "aerosols"
}

# === HELPER: Check if something is a single readable word ===
def is_single_skippable_word(value):
    return re.fullmatch(r"[a-zA-Z]+", value) and value.lower() in skip_values

# === MAIN LOGIC TO PROCESS EACH SCAN NAME ===
def update_scan_names(df, code_map, column="normalizedScan"):
    updated = []

    for val in df.get(column, []):
        val_str = str(val).strip()
        original_str = val_str

        # Step 1: Strip ^ and $ if present
        if re.fullmatch(r"^\^.*\$$", val_str):
            stripped_code = val_str[1:-1]
        else:
            stripped_code = val_str

        stripped_normalized = stripped_code.lower()

        # Step 2: Skip known single descriptive words (even if wrapped)
        if is_single_skippable_word(stripped_code):
            updated.append(original_str)
            continue

        # Step 3: Match known code
        if stripped_normalized in code_map:
            updated.append(f"{original_str} {code_map[stripped_normalized]}")
        elif re.fullmatch(r"[a-zA-Z0-9]+", stripped_code):
            updated.append(f"{original_str} Code not found")
        else:
            updated.append(original_str)

    df[column] = updated
    return df

# === MAIN WORKFLOW ===
def main():
    print(f"Loading code mappings from: {CODES_FILE}")
    code_map = load_code_map(CODES_FILE)

    print(f"Reading Excel file: {EXCEL_FILE} (Sheet: {SHEET_NAME})")
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    except ValueError as e:
        print(f"Error: Sheet '{SHEET_NAME}' not found - {e}")
        return

    if 'normalizedScan' not in df.columns:
        print("Error: Column 'normalizedScan' not found in the Excel sheet.")
        return

    print("Updating normalizedScan values...")
    df = update_scan_names(df, code_map)

    print(f"Saving updated Excel file to: {OUTPUT_FILE}")
    with pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=SHEET_NAME, index=False)

    print("Done. File saved at:", OUTPUT_FILE)

if __name__ == "__main__":
    main()
