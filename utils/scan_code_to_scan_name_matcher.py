import pandas as pd
import os

# File paths
source_file = r"C:\Users\Shaalan\tracking_openai\data\pvr_config_data\scan_groups_to_be_update150425.csv"
lookup_file = r"C:\Users\Shaalan\tracking_openai\data\pvr_config_data\scan-groups.csv"

# Load data
source_df = pd.read_csv(source_file)
lookup_df = pd.read_csv(lookup_file)

# Create lowercase versions of the columns used for matching
source_df['proposed_scan_group_lower'] = source_df['proposed_scan_group'].str.lower().str.strip()
lookup_df['scan_group_lower'] = lookup_df['scan_group'].str.lower().str.strip()

# Merge on the lowercase versions
merged_df = source_df.merge(
    lookup_df[['scan_group_lower', 'scanGroupId']],
    left_on='proposed_scan_group_lower',
    right_on='scan_group_lower',
    how='left'
)

# Clean up extra columns
merged_df.drop(columns=['proposed_scan_group_lower', 'scan_group_lower'], inplace=True)

# Save to new file
base, ext = os.path.splitext(source_file)
output_file = base + "_with_ids" + ext
merged_df.to_csv(output_file, index=False, encoding='utf-8')

print(f"✅ File saved with case-insensitive matching: {output_file}")
