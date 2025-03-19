import pymongo
from datetime import datetime
from dateutil.parser import isoparse
from tqdm import tqdm

def parse_mongo_timestamp(ts_value):
    if isinstance(ts_value, dict) and "$date" in ts_value:
        ts_str = ts_value["$date"]
    elif isinstance(ts_value, str):
        ts_str = ts_value
    else:
        # Not a recognizable timestamp format
        return datetime.min

    try:
        return isoparse(ts_str)
    except Exception:
        return datetime.min

def process_historical_shipments(mongo_uri="mongodb://localhost:27017/"):
    client = pymongo.MongoClient(mongo_uri)
    db = client["shipment_tracking"]
    shipments_collection = db["shipments"]

    total_shipments = shipments_collection.count_documents({})
    print(f"Processing {total_shipments} shipments to create sequential scan batch collections...")

    cursor = shipments_collection.find({})
    shipments = []
    max_scans = 0

    # ---------------------------------------
    # 1) Load & Sort Each Shipment's Scans
    # ---------------------------------------
    for shipment in tqdm(cursor, total=total_shipments, desc="Loading Shipments", unit="shipment"):
        scans = shipment.get("scans", [])
        if not scans:
            continue

        # Sort by timestamp ascending, tie-break by original array order (stable sort)
        # enumerate to preserve original indices for ties.
        enumerated_scans = list(enumerate(scans))
        enumerated_scans_sorted = sorted(
            enumerated_scans,
            key=lambda x: (parse_mongo_timestamp(x[1].get("timestamp")), x[0])
        )
        # Rebuild a sorted list of scan dicts
        sorted_scans = [item[1] for item in enumerated_scans_sorted]

        # Replace the original scans list with the sorted version
        shipment["scans"] = sorted_scans

        # Keep track of the maximum number of scans across all shipments
        max_scans = max(max_scans, len(sorted_scans))
        shipments.append(shipment)

    print(f"🔍 Maximum number of scans found among shipments: {max_scans}")

    # ---------------------------------------
    # 2) Build all partial-scan variations
    # ---------------------------------------
    all_variations = {}
    for scan_idx in range(1, max_scans + 1):
        collection_name = f"shipment_variations_batch_v2_{scan_idx}"
        variations = []

        for shipment in shipments:
            scans = shipment["scans"]
            # Only proceed if this shipment has at least `scan_idx` scans
            if len(scans) >= scan_idx:
                # partial_scans = first N scans
                partial_scans = scans[:scan_idx]

                variations.append({
                    "tracking_number": shipment["tracking_number"],
                    "carrier": shipment.get("carrier"),
                    # ... you can include other top-level fields as needed ...
                    "scans": partial_scans
                })

        if variations:
            all_variations[collection_name] = variations
            print(f"✅ Prepared {len(variations)} shipments for '{collection_name}'.")

    # ---------------------------------------
    # 3) Prompt for Confirmation
    # ---------------------------------------
    user_input = input("\nProceed with saving all batches? (yes/no): ").strip().lower()
    if user_input == "yes":
        for collection_name, docs in all_variations.items():
            db[collection_name].drop()  # Overwrite existing collection
            db[collection_name].insert_many(docs)
            print(f"✅ Saved {len(docs)} shipment variations into '{collection_name}'.")
        print("✅ All historical shipment batches saved successfully.")
    else:
        print("❌ Operation canceled. No changes were made.")


if __name__ == "__main__":
    process_historical_shipments("mongodb://localhost:27017/")