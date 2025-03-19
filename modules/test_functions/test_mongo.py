from modules.mongo_handler import get_mongo_connection

# Try connecting to MongoDB
client, db = get_mongo_connection()

print("✅ Connected to MongoDB")
print("📂 Available Collections:", db.list_collection_names())  # List all collections
