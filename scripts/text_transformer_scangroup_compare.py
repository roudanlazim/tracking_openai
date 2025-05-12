import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Path to the Excel file
excel_path = r"G:\Shared drives\Tech\PVR analysis\Tracking\PVR Scan Configuration\Scan group analysis\Scan group vs smart scan.xlsx"

xls = pd.ExcelFile(excel_path)
print("Available sheet names:", xls.sheet_names)

# Load Smart Scans and Scan Groups from correct sheets
smart_scans_df = pd.read_excel(excel_path, sheet_name="smartscan_list")
scan_groups_df = pd.read_excel(excel_path, sheet_name="scan_groups_list")

# Assuming the first column in each sheet contains the relevant text
smart_scans = smart_scans_df.iloc[:, 0].dropna().astype(str).tolist()
scan_groups = scan_groups_df.iloc[:, 0].dropna().astype(str).tolist()

# Load sentence transformer model
print("Loading semantic model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode sentences
print("Encoding scan group and smart scan entries...")
smart_embeddings = model.encode(smart_scans, convert_to_tensor=True)
group_embeddings = model.encode(scan_groups, convert_to_tensor=True)

# Perform matching
print("Matching each scan group to the closest smart scan...")
results = []
for i, group in enumerate(scan_groups):
    scores = util.cos_sim(group_embeddings[i], smart_embeddings)[0]
    best_idx = scores.argmax()
    best_score = float(scores[best_idx])
    best_match = smart_scans[best_idx]
    results.append({
        "Scan Group": group,
        "Best Matching Smart Scan": best_match,
        "Semantic Similarity": round(best_score, 3),
        "Needs Review (<0.8)": "✅" if best_score < 0.8 else ""
    })

# Output results
results_df = pd.DataFrame(results)
print("\n📋 Top Semantic Matches:")
print(results_df.to_string(index=False))

# ✅ Save results to a new sheet in the same Excel file
print("\nSaving results to Excel...")
with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    results_df.to_excel(writer, sheet_name="semantic_matches", index=False)

print("✅ Done! Results written to sheet 'semantic_matches'")
