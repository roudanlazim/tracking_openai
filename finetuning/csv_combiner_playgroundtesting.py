import pandas as pd
import glob
import os
import re

def build_scans_string(row, pairs):
    """
    Given a list of (timestamp_col, scan_col) pairs in ascending order,
    build a single string like:
      "(tsVal) scanVal,(tsVal2) scanVal2, ..."
    Return (combined_string, final_scan, scan_count).
    """
    parts = []
    last_scan = None
    count_scans = 0
    
    for (ts_col, scan_col) in pairs:
        ts_val   = row.get(ts_col, None)
        scan_val = row.get(scan_col, None)
        
        # Check if we have a non-empty scan
        if pd.notnull(scan_val) and str(scan_val).strip():
            ts_str = f"({ts_val})" if pd.notnull(ts_val) else "(UnknownTime)"
            scan_str = str(scan_val).strip()
            # e.g. "(2025-03-26T14:15:08) In Transit"
            parts.append(f"{ts_str} {scan_str}")
            last_scan = scan_str
            count_scans += 1

    combined = ",".join(parts)
    final_scan = last_scan if last_scan else ""
    return combined, final_scan, count_scans

def process_csv(file_path):
    """
    1) Read a single CSV
    2) Find columns matching "scans[ i ].timestamp" and "scans[ i ].scan"
    3) Build a DataFrame with columns: _id, tracking_number, carrier, scans, scan_group, scan_count
    """
    df = pd.read_csv(file_path)
    
    # Ensure columns exist for _id, tracking_number, and carrier (fallback to None if missing)
    if "_id" not in df.columns:
        df["_id"] = None
    if "tracking_number" not in df.columns:
        df["tracking_number"] = None
    if "carrier" not in df.columns:
        df["carrier"] = None

    # Drop columns that are entirely empty
    df.dropna(axis=1, how='all', inplace=True)

    # Regex to match "scans[\d+].timestamp" and "scans[\d+].scan"
    ts_pattern   = re.compile(r"^scans\[(\d+)\]\.timestamp$")
    scan_pattern = re.compile(r"^scans\[(\d+)\]\.scan$")

    # Dictionaries keyed by the numeric index inside the brackets
    timestamp_map = {}
    scan_map = {}

    # Find columns that match the above regex patterns
    for col in df.columns:
        m_ts = ts_pattern.match(col)
        if m_ts:
            idx = int(m_ts.group(1))
            timestamp_map[idx] = col
            continue
        
        m_scan = scan_pattern.match(col)
        if m_scan:
            idx = int(m_scan.group(1))
            scan_map[idx] = col
            continue

    # Build a sorted list of pairs (timestamp_col, scan_col)
    all_pairs = []
    # Only pair up indices that exist for both .timestamp AND .scan
    common_indices = sorted(set(timestamp_map.keys()) & set(scan_map.keys()))
    for i in common_indices:
        ts_col   = timestamp_map[i]
        scan_col = scan_map[i]
        all_pairs.append((ts_col, scan_col))

    # Construct final records
    records = []
    for _, row in df.iterrows():
        scans_str, final_scan, sc_count = build_scans_string(row, all_pairs)
        records.append({
            "_id": row.get("_id", ""),
            "tracking_number": row.get("tracking_number", ""),
            "carrier": row.get("carrier", ""),
            "scans": scans_str,       # e.g. "(tsVal) someScan,(tsVal2) secondScan"
            "scan_group": final_scan, # last non-empty scan
            "scan_count": sc_count
        })

    out_df = pd.DataFrame(records, columns=[
        "_id", "tracking_number", "carrier", "scans", "scan_group", "scan_count"
    ])
    return out_df

def main():
    input_folder = r"C:\Users\Shaalan\tracking_openai\data\training\train_datasets\rawsets_scangroup_specific_end"
    output_path  = r"C:\Users\Shaalan\tracking_openai\data\training\combined_scans.csv"

    # 1) Find all CSVs in the folder
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    if not csv_files:
        print("No CSV files found in the folder.")
        return

    # 2) Let the user pick which CSVs to combine
    #    Show a numbered list of CSV files
    print("Found CSV files:")
    for i, fpath in enumerate(csv_files):
        print(f"[{i}] {os.path.basename(fpath)}")

    selected_input = input(
        "\nEnter the indices of the files you want to combine (e.g., '0,2,4') or 'all' to process all:\n> "
    )
    
    # 3) Parse user selection
    if selected_input.strip().lower() == "all":
        selected_indices = range(len(csv_files))  # all files
    else:
        # Convert user input "0,2,4" into a list of ints [0, 2, 4]
        selected_indices = [int(x.strip()) for x in selected_input.split(",") if x.strip().isdigit()]
    
    chosen_files = []
    for idx in selected_indices:
        if 0 <= idx < len(csv_files):
            chosen_files.append(csv_files[idx])
        else:
            print(f"Warning: index {idx} is out of range")

    if not chosen_files:
        print("No valid files selected.")
        return

    print("\nYou chose the following files:")
    for f in chosen_files:
        print(" -", os.path.basename(f))
    
    # 4) Process each chosen file and combine results
    all_dfs = []
    for csv_file in chosen_files:
        print(f"\nProcessing {os.path.basename(csv_file)} ...")
        df_out = process_csv(csv_file)
        all_dfs.append(df_out)

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
    else:
        # If there's nothing to combine
        final_df = pd.DataFrame(columns=["_id","tracking_number","carrier","scans","scan_group","scan_count"])

    # 5) Save to output_path
    final_df.to_csv(output_path, index=False)
    print(f"\nSaved combined CSV to {output_path}")

if __name__ == "__main__":
    main()
