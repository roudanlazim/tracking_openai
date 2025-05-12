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
    return combined, (last_scan if last_scan else ""), count_scans

def process_csv(file_path):
    """
    1) Read a single CSV
    2) Find columns matching "scans[ i ].timestamp" and "scans[ i ].scan"
    3) Build final DataFrame with columns:
       _id, tracking_number, carrier, scans, scan_group, scan_count
    """
    df = pd.read_csv(file_path)
    
    # Ensure columns exist for _id, tracking_number, and carrier
    if "_id" not in df.columns:
        df["_id"] = None
    if "tracking_number" not in df.columns:
        df["tracking_number"] = None
    if "carrier" not in df.columns:
        df["carrier"] = None

    # Drop completely empty columns
    df.dropna(axis=1, how='all', inplace=True)

    # Regex to match "scans[\d+].timestamp" and "scans[\d+].scan"
    ts_pattern   = re.compile(r"^scans\[(\d+)\]\.timestamp$")
    scan_pattern = re.compile(r"^scans\[(\d+)\]\.scan$")

    # We will collect matches in dictionaries keyed by the numeric index
    timestamp_map = {}
    scan_map = {}

    # Loop over all columns to find those that match
    for col in df.columns:
        m_ts = ts_pattern.match(col)
        if m_ts:
            idx = int(m_ts.group(1))  # the capture group for the number
            timestamp_map[idx] = col
            continue
        
        m_scan = scan_pattern.match(col)
        if m_scan:
            idx = int(m_scan.group(1))
            scan_map[idx] = col
            continue

    # Build sorted list of pairs (ts_col, scan_col), ascending by index
    all_pairs = []
    for i in sorted(set(timestamp_map.keys()) & set(scan_map.keys())):
        # only if we have BOTH a timestamp and a scan for this index
        ts_col   = timestamp_map[i]
        scan_col = scan_map[i]
        all_pairs.append((ts_col, scan_col))

    # Build new rows
    records = []
    for _, row in df.iterrows():
        scans_str, final_scan, sc_count = build_scans_string(row, all_pairs)
        records.append({
            "_id": row.get("_id", ""),
            "tracking_number": row.get("tracking_number", ""),
            "carrier": row.get("carrier", ""),
            "scans": scans_str,        # e.g. "(tsVal) someScan,(tsVal2) secondScan"
            "scan_group": final_scan,  # last non-empty scan
            "scan_count": sc_count
        })

    # Construct final DataFrame
    out_df = pd.DataFrame(records, columns=[
        "_id",
        "tracking_number",
        "carrier",
        "scans",
        "scan_group",
        "scan_count"
    ])
    return out_df

def main():
    input_folder = r"C:\Users\Shaalan\tracking_openai\data\training\train_datasets\rawsets_scangroup_specific_end"
    output_path  = r"C:\Users\Shaalan\tracking_openai\data\training\combined_scans.csv"

    # Collect all CSV files
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    if not csv_files:
        print("No CSV files found.")
        return

    # Process each CSV, store results
    all_dfs = []
    for csv_file in csv_files:
        df_out = process_csv(csv_file)
        all_dfs.append(df_out)

    # Combine into one DataFrame
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
    else:
        final_df = pd.DataFrame(columns=["_id","tracking_number","carrier","scans","scan_group","scan_count"])

    # Save
    final_df.to_csv(output_path, index=False)
    print(f"Saved combined CSV to {output_path}")

if __name__ == "__main__":
    main()
