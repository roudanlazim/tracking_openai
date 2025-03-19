import pymongo
import logging
from datetime import datetime

PROMPT_DIR = "data/prompts/"


# =================================
# 1) Configuration
# =================================
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "shipment_tracking"  # <-- Adjust as needed

# =================================
# 2) Logging Setup
# =================================
logging.basicConfig(
    filename="mongo_operations.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =================================
# 3) Global MongoDB Client
# =================================
_mongo_client = None

def get_mongo_connection():
    """
    Returns a singleton MongoDB client and the specified database instance.
    """
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = pymongo.MongoClient(MONGO_URI)
        logging.info("✅ Created new MongoDB client.")
    return _mongo_client, _mongo_client[DB_NAME]

def get_collection(collection_name: str):
    """
    Returns a MongoDB collection handle for the given collection name.
    """
    _, db = get_mongo_connection()
    return db[collection_name]

def fetch_filtered_shipments(collection_name: str, batch_size=10):
    """
    Fetches shipments, EXCLUDING any that contain 'in transit' scans.
    Returns a list of formatted shipments.
    """
    collection_name = "shipment_variations_batch_1"
    collection = get_collection(collection_name)
    shipments = list(collection.find().limit(batch_size))

    formatted_shipments = []
    for shipment in shipments:
        scan_texts = [scan["scan"].lower() for scan in shipment.get("scans", [])]

        # 🚨 Exclude shipments that have 'in transit' anywhere
        if "in transit" in scan_texts:
            logging.info(f"🚨 Skipping shipment {shipment['tracking_number']} due to 'in transit' scan.")
            continue  # Skip this shipment

        formatted_shipments.append({
            "tracking_number": shipment.get("tracking_number"),
            "shipment_id": shipment.get("shipment_id"),
            "carrier": shipment.get("carrier"),
            "scans": shipment.get("scans", [])
        })

    logging.info(f"🔍 Retrieved {len(formatted_shipments)} valid shipments.")
    return formatted_shipments

def store_ai_results(collection_name: str, ai_results: list):
    """
    Stores AI-generated results into MongoDB, mapped to original shipments.
    """
    collection_name = "shipment_variations_batch_1"
    collection = get_collection(collection_name)
    if ai_results:
        collection.insert_many(ai_results)
        logging.info(f"✅ Stored {len(ai_results)} AI results in '{collection_name}'.")

def create_collection_if_not_exists(collection_name: str):
    """
    Creates a MongoDB collection if it does not exist yet.
    Returns the collection handle.
    """
    client, db = get_mongo_connection()
    # If collection already exists, just return it
    if collection_name in db.list_collection_names():
        logging.info(f"✅ Collection '{collection_name}' already exists.")
        return db[collection_name]
    # Otherwise create it by inserting an empty doc
    db[collection_name].insert_one({"created_at": datetime.utcnow()})
    logging.info(f"🆕 Created new collection '{collection_name}'.")
    return db[collection_name]

def drop_collection(collection_name: str):
    """
    Drops the specified collection (use with caution).
    """
    client, db = get_mongo_connection()
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        logging.info(f"❌ Dropped collection '{collection_name}'.")
    else:
        logging.warning(f"⚠️ Collection '{collection_name}' does not exist. Nothing to drop.")

def insert_documents(collection_name: str, documents: list):
    """
    Inserts multiple documents into the specified collection.
    documents should be a list of dicts.
    """
    if not documents:
        logging.warning("⚠️ No documents to insert. Operation skipped.")
        return
    collection = get_collection(collection_name)
    result = collection.insert_many(documents)
    logging.info(f"✅ Inserted {len(result.inserted_ids)} documents into '{collection_name}'.")

def find_documents(collection_name: str, filter_query=None, projection=None):
    """
    Finds documents in the specified collection matching filter_query.
    Optionally limit fields with projection.
    Returns a list of documents.
    """
    collection = get_collection(collection_name)
    if filter_query is None:
        filter_query = {}
    docs = list(collection.find(filter_query, projection))
    logging.info(f"🔎 Found {len(docs)} documents in '{collection_name}'.")
    return docs

def update_documents(collection_name: str, filter_query: dict, update_data: dict, many=False):
    """
    Updates documents in the specified collection that match filter_query with update_data.
    If many=False (default), updates the first matching document.
    If many=True, updates all matching documents.
    """
    collection = get_collection(collection_name)
    if many:
        result = collection.update_many(filter_query, {"$set": update_data})
        logging.info(f"✅ update_many => Matched {result.matched_count}, Modified {result.modified_count} in '{collection_name}'.")
    else:
        result = collection.update_one(filter_query, {"$set": update_data})
        logging.info(f"✅ update_one => Matched {result.matched_count}, Modified {result.modified_count} in '{collection_name}'.")

def count_documents(collection_name: str, filter_query=None):
    """
    Returns the count of documents matching filter_query in the specified collection.
    """
    collection = get_collection(collection_name)
    if filter_query is None:
        filter_query = {}
    count = collection.count_documents(filter_query)
    logging.info(f"🔢 Counted {count} documents in '{collection_name}' with filter {filter_query}.")
    return count

