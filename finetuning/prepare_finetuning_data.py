import pymongo
import json

def prepare_finetuning_data(mongo_uri, output_file="fine_tuning_data.jsonl"):
    """Prepares structured data for fine-tuning a model based on verified clusters."""
    client = pymongo.MongoClient(mongo_uri)
    db = client["shipment_tracking"]
    clusters_collection = db["clusters"]

    with open(output_file, "w", encoding="utf-8") as f:
        for cluster in clusters_collection.find({}):
            entry = {
                "messages": [
                    {"role": "user", "content": f"Shipment history:\n{cluster['label']}\nPredict the final status."},
                    {"role": "assistant", "content": cluster["label"]}
                ]
            }
            f.write(json.dumps(entry) + "\n")

    print(f"✅ Fine-tuning data saved to {output_file}.")

if __name__ == "__main__":
    prepare_finetuning_data("mongodb://localhost:27017/")
