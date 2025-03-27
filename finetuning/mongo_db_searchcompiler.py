import csv
import re

from pymongo import MongoClient
from bson import ObjectId
from mongo_query import query
from datetime import datetime

# === CONFIGURATION ===
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "shipment_tracking"
COLLECTION_PATTERN = re.compile(r"shipment_variations_batch_v2_\d+$")
PER_COLLECTION_LIMIT = 10

today_str = datetime.today().strftime("%Y-%m-%d")
OUTPUT_FILE = fr"C:\Users\Shaalan\tracking_openai\data\training\exported_data_{today_str}.csv"

# === CONNECT TO MONGO ===
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# === IDENTIFY TARGET COLLECTIONS ===
all_collections = db.list_collection_names()
target_collections = [coll for coll in all_collections if COLLECTION_PATTERN.match(coll)]

results = []
max_scans_seen = 0

for collection_name in sorted(target_collections):
    collection = db[collection_name]
    cursor = collection.find(query).limit(PER_COLLECTION_LIMIT)

    for doc in cursor:
        row = {
            "_id": str(doc.get("_id", ObjectId())),
            "tracking_number": doc.get("tracking_number", ""),
            "carrier": doc.get("carrier", "")
        }

        scans = doc.get("scans", [])
        max_scans_seen = max(max_scans_seen, len(scans))

        for i, scan in enumerate(scans):
            ts = scan.get("timestamp")
            sc = scan.get("scan")
            if ts:
                row[f"scans[{i}].timestamp"] = ts.isoformat()
            if sc:
                row[f"scans[{i}].scan"] = sc

        results.append(row)

# === Dynamic Column Headers ===
fieldnames = ["_id", "tracking_number", "carrier"]
for i in range(max_scans_seen):
    fieldnames.append(f"scans[{i}].timestamp")
    fieldnames.append(f"scans[{i}].scan")

# === WRITE TO CSV ===
with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"✅ Exported {len(results)} documents to '{OUTPUT_FILE}' using current query.")