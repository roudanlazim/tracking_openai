import tiktoken
import json
import os

# Path to your JSONL file (update if needed)
jsonl_path = "data/training_data_stage1.jsonl"  # Change the path if necessary

# Load the tokenizer for GPT-3.5 Turbo (works for GPT-4 Turbo too)
tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Initialize token counter
total_tokens = 0

# Read and process the JSONL file
try:
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)  # Parse JSON line
            messages = data.get("messages", [])
            for message in messages:
                total_tokens += len(tokenizer.encode(message["content"]))  # Count tokens

    # OpenAI Pricing for Fine-Tuning (GPT-3.5 Turbo & GPT-4 Turbo)
    cost_per_1000_tokens = 0.008  # Fine-tuning cost per 1,000 tokens

    # Estimate the total cost
    estimated_cost = (total_tokens / 1000) * cost_per_1000_tokens

    # Print Results
    print("\n🔹 Fine-Tuning Cost Estimator")
    print(f"📄 File: {jsonl_path}")
    print(f"🔢 Total Tokens: {total_tokens}")
    print(f"💰 Estimated Fine-Tuning Cost: ${estimated_cost:.2f} (GPT-3.5 Turbo)")

except FileNotFoundError:
    print(f"❌ ERROR: File not found at {jsonl_path}. Please check the file path.")
except json.JSONDecodeError:
    print(f"❌ ERROR: Invalid JSON format in {jsonl_path}.")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
