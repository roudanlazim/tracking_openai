import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Path to the Excel file
excel_path = r"G:\Shared drives\Tech\PVR analysis\Tracking\PVR Scan Configuration\Scan group analysis\Scan group vs smart scan.xlsx"

# Check available sheets
xls = pd.ExcelFile(excel_path)
print("Available sheet names:", xls.sheet_names)

# Load the relevant sheets
smart_scans_df = pd.read_excel(excel_path, sheet_name="smartscan_list")
scan_groups_df = pd.read_excel(excel_path, sheet_name="scan_groups_list")

# Extract text data
smart_scans = smart_scans_df.iloc[:, 0].dropna().astype(str).tolist()
scan_groups = scan_groups_df.iloc[:, 0].dropna().astype(str).tolist()

# Load the semantic model
print("Loading sentence-transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode sentences into semantic vectors
print("Encoding smart scans and scan groups...")
smart_embeddings = model.encode(smart_scans, convert_to_tensor=True)
group_embeddings = model.encode(scan_groups, convert_to_tensor=True)

# Perform reverse matching: each smart scan gets its best-matching scan group
print("Matching each smart scan to the closest scan group...")
reverse_results = []
for i, smart in enumerate(smart_scans):
    scores = util.cos_sim(smart_embeddings[i], group_embeddings)[0]
    best_idx = scores.argmax()
    best_score = float(scores[best_idx])
    best_match = scan_groups[best_idx]
    reverse_results.append({
        "Smart Scan": smart,
        "Best Matching Scan Group": best_match,
        "Semantic Similarity": round(best_score, 3),
        "Needs Review (<0.8)": "✅" if best_score < 0.8 else ""
    })

# Print summary
reverse_df = pd.DataFrame(reverse_results)
print("\n📋 Reverse Semantic Matches (Smart ➝ Group):")
print(reverse_df.to_string(index=False))

# Save to a new sheet
print("\nSaving reverse matches to Excel...")
with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    reverse_df.to_excel(writer, sheet_name="reverse_matches", index=False)

print("✅ Done! Reverse matches written to 'reverse_matches' sheet.")
