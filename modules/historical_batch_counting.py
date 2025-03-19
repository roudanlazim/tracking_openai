import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["shipment_tracking"]
shipments_collection = db["shipments"]

# Retrieve all shipments and calculate batch count
cursor = shipments_collection.find({}, {"scans": 1})
total_shipments = shipments_collection.count_documents({})

# Determine actual max scans
max_scans = 0

for shipment in cursor:
    scan_length = len(shipment.get("scans", []))
    max_scans = max(max_scans, scan_length)

# Ensure the max scan count is within a reasonable range
max_scan_threshold = 100  # Define a reasonable upper limit

if max_scans > max_scan_threshold:
    print(f"⚠ Warning: Detected an unusually high scan count ({max_scans}). This might indicate an error.")
    max_scans = max_scan_threshold

# Display results
print(f"✅ Total Shipments: {total_shipments}")
print(f"✅ Actual Maximum Scans in a Single Shipment: {max_scans}")
print(f"✅ Expected Total Batches: {max_scans}")
