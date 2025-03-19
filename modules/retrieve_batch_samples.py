import pymongo

def get_batches(mongo_uri, db_name="shipment_tracking"):
    """Retrieves all batch collections dynamically."""
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    
    # Find all collections matching batch pattern
    batch_collections = [col for col in db.list_collection_names() if col.startswith("shipment_variations_batch_")]

    if not batch_collections:
        print("⚠ No batch collections found.")
        return []

    print(f"📦 Found {len(batch_collections)} batch collections:\n{batch_collections}")
    return batch_collections

def retrieve_sample_shipments(mongo_uri, num_samples=5):
    """Retrieves the same 5 example shipments from all batch collections."""
    client = pymongo.MongoClient(mongo_uri)
    db = client["shipment_tracking"]
    
    batch_collections = get_batches(mongo_uri)

    if not batch_collections:
        return

    all_samples = {}

    for batch in batch_collections:
        print(f"\n🔍 Retrieving {num_samples} shipments from `{batch}`...")
        
        # Fetch 5 example shipments
        example_shipments = list(db[batch].find().limit(num_samples))
        
        if example_shipments:
            all_samples[batch] = example_shipments
            print(f"✅ Retrieved {len(example_shipments)} shipments from `{batch}`.")
        else:
            print(f"⚠ No shipments found in `{batch}`.")

    return all_samples

if __name__ == "__main__":
    mongo_uri = "mongodb://localhost:27017/"
    
    # Retrieve and display shipments
    batch_samples = retrieve_sample_shipments(mongo_uri)

    if batch_samples:
        for batch, shipments in batch_samples.items():
            print(f"\n📦 **Batch: {batch}**")
            for i, shipment in enumerate(shipments, start=1):
                print(f"\n🚚 Example Shipment {i}:")
                print(shipment)
