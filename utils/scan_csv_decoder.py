import pandas as pd
import os
import re

# === HARD-CODED PATHS ===
DATA_DIR = r"C:\Users\Shaalan\tracking_openai\data\pvr_config_data"
CODES_FILE = os.path.join(DATA_DIR, "scan_codes.csv")

# === SKIP LIST ===
skip_values = {
    "delivery", "damaged", "recogido", "transit", "lost", "money", "carded",
    "top", "bottom", "button", "leg", "door", "none", "bell", "deadline", "deadlines",
    "stopped", "missort", "liquid", "aerosols"
}

def is_single_skippable_word(value):
    return re.fullmatch(r"[a-zA-Z]+", value) and value.lower() in skip_values

# === LOAD CODE MAP ===
def load_code_map(path):
    try:
        df = pd.read_csv(path).applymap(str)
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="ISO-8859-1").applymap(str)

    return {
        str(row['code']).strip().lower(): str(row['scan']).strip()
        for _, row in df.iterrows()
    }

# === UPDATE COLUMN FUNCTION ===
def create_decoded_column(df, code_map, column):
    new_column = f"{column}_decoded"
    updated = []

    for val in df.get(column, []):
        val_str = str(val).strip()
        original_str = val_str

        if re.fullmatch(r"^\^.*\$$", val_str):
            stripped_code = val_str[1:-1]
        else:
            stripped_code = val_str

        stripped_normalized = stripped_code.lower()

        if is_single_skippable_word(stripped_code):
            updated.append(original_str)
        elif stripped_normalized in code_map:
            updated.append(f"{original_str} {code_map[stripped_normalized]}")
        elif re.fullmatch(r"[a-zA-Z0-9]+", stripped_code):
            updated.append(f"{original_str} Code not found")
        else:
            updated.append(original_str)

    df[new_column] = updated
    return df

# === FILE DISCOVERY + USER CHOICE ===
def select_file():
    all_files = [f for f in os.listdir(DATA_DIR) if f.endswith((".csv", ".xlsx"))]
    if not all_files:
        print("No CSV or Excel files found in directory.")
        return None, None

    print("\nAvailable data files:")
    for i, f in enumerate(all_files, 1):
        print(f"{i}: {f}")

    file_idx = int(input("\nSelect a file by number: ")) - 1
    selected_file = all_files[file_idx]
    file_path = os.path.join(DATA_DIR, selected_file)
    return file_path, selected_file

# === SELECT COLUMN ===
def select_column(df):
    print("\nAvailable columns:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i}: {col}")

    col_idx = int(input("\nSelect a column to decode by number: ")) - 1
    return df.columns[col_idx]

# === MAIN LOGIC ===
def main():
    print(f"Using code mapping file: {CODES_FILE}")
    code_map = load_code_map(CODES_FILE)

    file_path, file_name = select_file()
    if not file_path:
        return

    ext = os.path.splitext(file_name)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        sheets = pd.ExcelFile(file_path).sheet_names
        print("\nAvailable sheets:")
        for i, sheet in enumerate(sheets, 1):
            print(f"{i}: {sheet}")
        sheet_idx = int(input("\nSelect a sheet by number: ")) - 1
        df = pd.read_excel(file_path, sheet_name=sheets[sheet_idx])
    else:
        print("Unsupported file type.")
        return

    column = select_column(df)
    print(f"\nDecoding column: {column}")

    df = create_decoded_column(df, code_map, column)

    # === OUTPUT FILE ===
    file_root, file_ext = os.path.splitext(file_path)
    output_path = f"{file_root}_decoded{file_ext}"
    print(f"\nSaving to: {output_path}")

    if ext == ".csv":
        df.to_csv(output_path, index=False)
    else:
        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name=sheets[sheet_idx], index=False)

    print("\nDone.")

if __name__ == "__main__":
    main()