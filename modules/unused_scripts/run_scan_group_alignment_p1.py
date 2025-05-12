import os
import json
import argparse
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
from modules.file_handler import apply_proposed_sg_to_csv
from modules.logging_utils import logger

# ✅ Load environment and OpenAI client
def load_api_key():
    dotenv_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
    load_dotenv(dotenv_path=dotenv_path)

    from modules.system_settings import SystemSettings
    api_key = os.getenv("OPENAI_API_KEY") or SystemSettings.api_key

    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY not found. Please set it in `.env` or via `SystemSettings`.")
    return api_key

client = OpenAI(api_key=load_api_key())
MODEL_NAME = "gpt-4o"

# ✅ File paths
SCAN_GROUPS_PATH = r"C:\Users\Shaalan\tracking_openai\data\pvr_config_data\scan-groups.csv"
MAPPING_CSV_PATH = r"C:\Users\Shaalan\tracking_openai\data\pvr_config_data\scan_group_mapping_export.csv"
OUTPUT_CSV_PATH = r"C:\Users\Shaalan\tracking_openai\data\pvr_config_data\scan-groups-aligned.csv"
LOG_BASE_DIR = r"C:\Users\Shaalan\tracking_openai\scripts\logs"

# ✅ Load scan groups from CSV
def load_scan_groups(path):
    print(f"Loading scan groups from: {path}")
    df = pd.read_csv(path)
    scan_groups = df["scan_group"].dropna().tolist()
    print(f"Loaded {len(scan_groups)} scan groups.")
    return scan_groups

# ✅ Load scan names from mapping CSV
def load_scans_to_align(path):
    print(f"📥 Loading scan names from: {path}")
    df = pd.read_csv(path)
    scan_names = df["scan_name"].dropna().tolist()
    print(f"✅ Loaded {len(scan_names)} scan names.")
    return scan_names

# ✅ Create structured GPT prompt
def create_prompt(scan_groups, scan_batch):
    system_prompt = system_prompt = system_prompt = (
    "You are a logistics AI assistant.\n\n"
    "Your task is to classify each raw carrier scan event into a predefined scan group.\n"
    "These scan events originate from different carriers with varied wording but represent common logistics updates.\n"
    "Your job is to normalize them into a consistent list of scan groups.\n\n"
    "Guidelines:\n"
    "1. Use ONLY one of the scan groups listed below (see 'Valid scan groups').\n"
    "2. Always choose the most semantically precise and granular group possible.\n"
    "3. If multiple scan groups could apply equally, return: \"unclear__['Group A', 'Group B']\"\n"
    "4. If the scan does not clearly match any group, return \"not_clear\".\n"
    "5. If the scan appears to describe a new event type not yet covered, return it with prefix: \"new__<label>\"\n"
    "6. Do NOT explain your reasoning. Output only the JSON object.\n"
    "7. Base your classification on the *meaning* or *intent*, not exact wording.\n"
    "8. Use 'Internal activity scan' only for system-level updates (e.g., data merges) that have no shipment-level meaning.\n"
    "9. Scans with 'sort facility' or 'sorting center' → classify as 'In Transit' unless it clearly says 'arrived' or 'departed'.\n"
    "10. 'Arrival at delivery depot' = package arriving at final local depot.\n"
    "11. 'Departure Scan' = package leaving any facility.\n"
    "12. Use 'In Transit' only when movement is implied but not explicitly described.\n"
    "13. If a scan mentions a 'sub-depot', 'hub', or 'sorting center', classify it as 'In Transit'. These are intermediate routing points and not final delivery depots.\n"
    "14. If a scan contains terms like 'parent-child', 'inbound receipt', or 'scan at depot' but lacks a final delivery context, classify it as 'In Transit'.\n"
    "15. If a scan mentions 'return', 'returns sort', or 'returns depot', classify as 'In Transit' **unless** the scan clearly indicates that the shipment has been returned, is being returned, or the return is requested (e.g., 'Return of the package requested', 'Return parcel now delivered back to sender').\n\n"
    "Valid scan groups:\n"

    f"{json.dumps(list(scan_groups), indent=2)}\n\n"
    "Return ONLY this JSON format:\n"
    "{\n"
    "  \"proposed_matches\": [\n"
    "    {\"original\": \"Scan Text 1\", \"proposed_sg\": \"Scan Group Name\"},\n"
    "    {\"original\": \"Scan Text 2\", \"proposed_sg\": \"Scan Group Name\"}\n"
    "  ]\n"
    "}\n\n"
    "Examples:\n"
    "[\n"
    "  {\"original\": \"edi invoice and hwb data merge\", \"proposed_sg\": \"Internal activity scan\"},\n"
    "  {\"original\": \"arrived at delivery facility\", \"proposed_sg\": \"Arrival at delivery depot\"},\n"
    "  {\"original\": \"transferred through facility\", \"proposed_sg\": \"In Transit\"},\n"
    "  {\"original\": \"delivery completed\", \"proposed_sg\": \"Delivered\"},\n"
    "  {\"original\": \"label created\", \"proposed_sg\": \"Shipment manifested\"},\n"
    "  {\"original\": \"departed from sorting center\", \"proposed_sg\": \"Departure Scan\"},\n"
    "  {\"original\": \"arrived at sort facility\", \"proposed_sg\": \"In Transit\"},\n"
    "  {\"original\": \"unable to deliver - customer not home\", \"proposed_sg\": \"unclear__['Delivery Attempted', 'Exception']\"},\n"
    "  {\"original\": \"located in depot returns sort\", \"proposed_sg\": \"In Transit\"},\n"
    "  {\"original\": \"return of the package requested\", \"proposed_sg\": \"Return of the package requested\"},\n"
    "  {\"original\": \"return parcel now delivered back to sender\", \"proposed_sg\": \"Return parcel now delivered back to sender\"},\n"
    "  {\"original\": \"return partially received\", \"proposed_sg\": \"Return partially received\"},\n"
    "  {\"original\": \"inbound parent-child at depot\", \"proposed_sg\": \"In Transit\"}\n"
    "]"
)
    user_message = json.dumps({
        "scans_to_classify": scan_batch
    }, indent=2)

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

# Log GPT request/response + token usage
def log_gpt_batch(batch_num, prompt_messages, response_data, script_name="run_scan_group_alignment"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(LOG_BASE_DIR, exist_ok=True)
    filename = f"{script_name}_batch{batch_num}_{timestamp}.json"
    path = os.path.join(LOG_BASE_DIR, filename)

    log_data = {
        "timestamp": timestamp,
        "batch_number": batch_num,
        "prompt": prompt_messages,
        "gpt_response": response_data.get("response_text", ""),
        "token_usage": response_data.get("token_usage", {})
    }

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
        print(f"Saved GPT log to: {path}")
    except Exception as e:
        print(f"Could not save GPT log: {e}")

# ✅ Call OpenAI with correct formatting and tracking
def get_proposed_matches(prompt):
    try:
        print("Sending prompt to GPT-4o...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=prompt,
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
        print("Response received.")

        usage = response.usage
        token_usage = {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        }

        return {
            "proposed_matches": json.loads(content).get("proposed_matches", []),
            "response_text": content,
            "token_usage": token_usage
        }

    except Exception as e:
        print(f"❌ GPT call failed: {e}")
        return {
            "proposed_matches": [],
            "response_text": "",
            "token_usage": {}
        }

# ✅ Main logic
def main(max_batches=None):
    print("🚀 Starting scan group alignment using GPT-4o...\n")

    scan_groups = load_scan_groups(SCAN_GROUPS_PATH)
    all_scans = load_scans_to_align(MAPPING_CSV_PATH)
    all_matches = []

    batch_size = 25
    total_batches = len(all_scans) // batch_size + int(len(all_scans) % batch_size != 0)
    if max_batches:
        total_batches = min(total_batches, max_batches)

    print(f"🔄 Processing {total_batches} batch(es) of up to {batch_size} scans each...\n")

    for i in tqdm(range(0, total_batches * batch_size, batch_size), desc="Aligning", unit="batch"):
        scan_batch = all_scans[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        print(f"\n📦 Batch {batch_num}: Sending {len(scan_batch)} scans")

        prompt = create_prompt(scan_groups, scan_batch)
        gpt_result = get_proposed_matches(prompt)
        log_gpt_batch(batch_num, prompt, gpt_result)

        if gpt_result["proposed_matches"]:
            print(f"✅ Batch {batch_num} returned {len(gpt_result['proposed_matches'])} matches")
        else:
            print(f"⚠️ Batch {batch_num} returned NO matches")

        all_matches.extend(gpt_result["proposed_matches"])

    print("\n💾 Writing final aligned CSV...")
    apply_proposed_sg_to_csv(
        mapping_csv_path=MAPPING_CSV_PATH,
        scan_groups_path=SCAN_GROUPS_PATH,
        output_csv_path=OUTPUT_CSV_PATH,
        proposed_matches=all_matches,
        run_label="gpt4o_test"
    )
    print(f"CSV written to: {OUTPUT_CSV_PATH}")
    print("🎉 Alignment complete!")

# CLI support
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GPT-based scan group alignment.")
    parser.add_argument("--max-batches", type=int, help="Limit how many batches to process.")
    args = parser.parse_args()
    main(max_batches=args.max_batches)