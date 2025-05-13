import os
import json
import time
import openai
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util

# ===== CONFIG =====
excel_path = r"G:\Shared drives\Tech\PVR analysis\Tracking\PVR Scan Configuration\Scan group analysis\scan_group_analysis.csv"
column_name = "scan_group"
output_dir = r"G:\Shared drives\Tech\PVR analysis\Tracking\PVR Scan Configuration\Scan group analysis"
similarity_threshold = 0.75
internal_similarity_threshold = 0.9
model_name = "gpt-4o"
embed_model_name = "all-MiniLM-L6-v2"
batch_size = 25
max_retries = 3
retry_backoff = 3.0

# ===== Load API Key =====
def load_api_key():
    dotenv_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
    load_dotenv(dotenv_path=dotenv_path)
    return os.getenv("OPENAI_API_KEY")

openai.api_key = load_api_key()

# ===== Progress States =====
progress_labels = [
    "InTransit", "TransitHold", "CustomsHold", "Delivered", "Manifested", "DroppedOff", 
    "ShipmentCancelled", "Collected", "OutForDelivery", "DeliveryHold", "Returned", 
    "CollectionAttemptedButFailed", "DeliveryAttemptedButFailed", "BeingReturned", 
    "PartiallyDelivered", "DiscardedAbandonedLost"
]

# ===== GPT Prompt Generator =====
def build_gpt_prompt(scan_batch: list[str]) -> list[dict]:
    user_prompt = (
        "You are a system that reformats logistics scan group labels. "
        "For each of the following scan labels, return a clean, structured version "
        "in the format '<Action> <Object> - <Qualifier>' if applicable. "
        "Do not repeat the original. Use natural phrasing.\n\n"
        "Return a JSON list under the key 'structured_names'.\n\n"
        f"Scan Labels: {json.dumps(scan_batch)}"
    )
    return [
        {"role": "system", "content": "You are an expert logistics classification assistant."},
        {"role": "user", "content": user_prompt}
    ]

# ===== GPT Call =====
def get_structured_names(messages):
    for attempt in range(1, max_retries + 1):
        try:
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=messages,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content.strip()
            return json.loads(content).get("structured_names", [])
        except Exception as e:
            print(f"GPT failed on attempt {attempt}: {e}")
            if attempt < max_retries:
                time.sleep(retry_backoff * attempt)
    return []

# ===== Main Execution =====
def main():
    print("🔹 Loading scan labels from CSV...")
    df = pd.read_csv(excel_path)
    scan_groups = df[column_name].dropna().astype(str).tolist()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(output_dir, f"scan_group_structured_{timestamp}.csv")
    print(f"🔸 Loaded {len(scan_groups)} entries.")

    # GPT: Batch structured name generation
    all_structured = []
    for i in tqdm(range(0, len(scan_groups), batch_size), desc="🚀 Generating Structured Names"):
        batch = scan_groups[i:i+batch_size]
        messages = build_gpt_prompt(batch)
        result = get_structured_names(messages)
        all_structured.extend(result if result else ["REVIEW: " + label for label in batch])

    df["Structured Name (AI Ready)"] = all_structured

    # Embedding model setup
    print("🔹 Loading embedding model...")
    model = SentenceTransformer(embed_model_name)
    sg_embeddings = model.encode(scan_groups, convert_to_tensor=True)
    struct_embeddings = model.encode(all_structured, convert_to_tensor=True)
    progress_embeddings = model.encode(progress_labels, convert_to_tensor=True)

    # Duplicate detection
    seen = set()
    duplicates = []
    for name in scan_groups:
        if name in seen:
            duplicates.append("Yes")
        else:
            duplicates.append("No")
            seen.add(name)
    df["Exact Duplicate"] = duplicates

    # Internal similarity
    similarity_flags = []
    for i, emb_i in enumerate(struct_embeddings):
        similar_count = 0
        for j, emb_j in enumerate(struct_embeddings):
            if i != j and float(util.cos_sim(emb_i, emb_j)[0]) >= internal_similarity_threshold:
                similar_count += 1
        similarity_flags.append("Yes" if similar_count > 0 else "No")
    df["Very Similar to Another Scan Group"] = similarity_flags

    # Progress classification
    print("🔹 Classifying progress...")
    assigned_progress = []
    similarity_scores = []
    vague_flags = []
    for i, emb in enumerate(struct_embeddings):
        scores = util.cos_sim(emb, progress_embeddings)[0]
        best_idx = scores.argmax()
        best_score = float(scores[best_idx])
        label = progress_labels[best_idx] if best_score >= similarity_threshold else "Uncertain"
        flag = "Yes" if best_score < similarity_threshold else ""
        assigned_progress.append(label)
        similarity_scores.append(round(best_score, 3))
        vague_flags.append(flag)

    df["Assigned Progress (Semantic Match)"] = assigned_progress
    df["Similarity Score (to Progress Definition)"] = similarity_scores
    df["Vague or Overlapping (Score < 0.75)"] = vague_flags

    # Output results
    print(f"✅ Writing output to: {output_file}")
    df.to_csv(output_file, index=False)

    print(f"\nSummary:")
    print(f"Total scan groups: {len(scan_groups)}")
    print(f"Structured names generated: {len(all_structured)}")
    print(f"Vague entries (score < {similarity_threshold}): {vague_flags.count('Yes')}")
    print(f"Exact duplicates: {duplicates.count('Yes')}")
    print(f"Internally similar scan groups: {similarity_flags.count('Yes')}")

if __name__ == "__main__":
    main()
