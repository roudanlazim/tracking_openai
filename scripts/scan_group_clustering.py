import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler
import umap
import hdbscan
from openpyxl import load_workbook

# Path to the Excel file
excel_path = r"G:\Shared drives\Tech\PVR analysis\Tracking\PVR Scan Configuration\Scan group analysis\Scan group vs smart scan.xlsx"

# Load workbook
xls = pd.ExcelFile(excel_path)
print("Available sheet names:", xls.sheet_names)

# Load the sg_final_renamed sheet (use the one you renamed already)
sg_final_df = pd.read_excel(excel_path, sheet_name="sg_final_renamed")

# Extract the renamed_sg_name column
sg_names = sg_final_df['renamed_sg_name'].dropna().astype(str).tolist()

# Load the upgraded semantic model
print("Loading semantic model...")
model = SentenceTransformer('all-mpnet-base-v2')

# Encode the scan group names
print("Encoding scan group names...")
sg_embeddings = model.encode(sg_names, convert_to_tensor=False)

# Dimensionality reduction
print("Running UMAP dimensionality reduction...")
umap_reducer = umap.UMAP(n_components=5, random_state=42)
embedding_umap = umap_reducer.fit_transform(sg_embeddings)

# Clustering
print("Running HDBSCAN clustering...")
clusterer = hdbscan.HDBSCAN(min_cluster_size=5, prediction_data=True)
cluster_labels = clusterer.fit_predict(embedding_umap)

# Assign Theme IDs
sg_final_df['theme_id'] = cluster_labels

# Predict 'Next Action Required' based on simple keyword rules
def next_action_required(name):
    name_lower = name.lower()
    # Define simple rules
    action_needed_keywords = ["failed", "awaiting", "held", "clearance", "pending", "missing", "unable", "re-attempt", "await", "refused", "delayed"]
    complete_keywords = ["delivered", "cancelled", "returned", "collected", "completed"]

    if any(keyword in name_lower for keyword in action_needed_keywords):
        return "Yes"
    elif any(keyword in name_lower for keyword in complete_keywords):
        return "No"
    else:
        return "Unknown"  # default if ambiguous

print("Predicting next action requirement...")
sg_final_df['next_action_required'] = sg_final_df['renamed_sg_name'].apply(next_action_required)

# Save results back to Excel
print("Saving grouped scan groups with next action prediction...")
with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    sg_final_df.to_excel(writer, sheet_name="sg_final_grouped", index=False)

print("✅ Done! Output written to sheet 'sg_final_grouped'")
