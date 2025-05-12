import pandas as pd
import re
import os
from sentence_transformers import SentenceTransformer, util
from openpyxl import load_workbook

# -------- SETTINGS --------

# Path to your Excel file
excel_path = r"G:\Shared drives\Tech\PVR analysis\Tracking\PVR Scan Configuration\Scan group analysis\Scan group vs smart scan.xlsx"

# Base name for saving versions
base_sheet_name = "sg_final_dedupe"

# Similarity threshold for flagging matches
similarity_threshold = 0.8

# Model to use
model_name = 'all-mpnet-base-v2'

# -------- SCRIPT --------

# Load the workbook and check available sheets
xls = pd.ExcelFile(excel_path)
existing_sheets = xls.sheet_names
print("Available sheet names:", existing_sheets)

# Load the source data
print("Loading source sheet 'sg_final'...")
sg_final_df = pd.read_excel(excel_path, sheet_name="sg_final")
sg_names = sg_final_df['sg_name'].dropna().astype(str).tolist()

# Load the semantic model
print(f"Loading semantic model: {model_name} ...")
model = SentenceTransformer(model_name)

# Encode all scan group names
print("Encoding scan group names...")
sg_embeddings = model.encode(sg_names, convert_to_tensor=True)

# Perform internal similarity matching
print("Comparing scan groups internally...")
match_results = []

for i, source_name in enumerate(sg_names):
    scores = util.cos_sim(sg_embeddings[i], sg_embeddings)[0]
    matched_names = []
    matched_scores = []

    for j, score in enumerate(scores):
        if i != j:  # Ignore self-match
            if score >= similarity_threshold:
                matched_names.append(sg_names[j])
                matched_scores.append(str(round(float(score), 3)))

    # Build results
    match_flag = "Yes" if matched_names else "No"
    match_names_str = ", ".join(matched_names)
    match_scores_str = ", ".join(matched_scores)

    match_results.append({
        "match": match_flag,
        "match_names": match_names_str,
        "match_scores": match_scores_str
    })

# Merge match results into the original DataFrame
match_df = pd.DataFrame(match_results)
output_df = pd.concat([sg_final_df.reset_index(drop=True), match_df], axis=1)

# -------- AUTO-VERSIONING --------

# Find existing sg_final_dedupe_vX sheets
pattern = re.compile(f"^{base_sheet_name}_v(\\d+)$")
existing_versions = [int(m.group(1)) for sheet in existing_sheets if (m := pattern.match(sheet))]
next_version = max(existing_versions, default=0) + 1
next_sheet_name = f"{base_sheet_name}_v{next_version}"

print(f"Saving to new sheet: {next_sheet_name}...")

# Save to Excel (append mode)
with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
    output_df.to_excel(writer, sheet_name=next_sheet_name, index=False)

print(f"✅ Done! Results written to '{next_sheet_name}'")
