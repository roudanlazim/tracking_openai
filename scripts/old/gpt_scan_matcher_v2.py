import os
import json
import argparse
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from datetime import datetime
import time
from openai import OpenAI

from modules.file_handler import apply_proposed_sg_to_csv
from modules.logging_utils import logger
from modules.system_settings import SystemSettings
from modules.prompt_generator import load_prompt_from_json
from modules.prompt_generator import generate_scan_prompt

# === Default Paths ===
DEFAULT_SCAN_GROUPS_PATH = r"C:\Users\Shaalan\tracking_openai\data\pvr_config_data\scan-groups.csv"
DEFAULT_MAPPING_CSV_PATH = r"C:\Users\Shaalan\tracking_openai\data\pvr_config_data\scan_group_mapping_export.csv"
DEFAULT_OUTPUT_CSV_PATH = r"C:\Users\Shaalan\tracking_openai\data\pvr_config_data\scan-groups-aligned.csv"
DEFAULT_PROMPT_PATH = r"C:\Users\Shaalan\tracking_openai\data\prompts\pvr_matcher_prompt\scan_group_prompt.json"
LOG_BASE_DIR = r"C:\Users\Shaalan\tracking_openai\scripts\logs"

MODEL_NAME = "gpt-4o-mini"
BATCH_SIZE = 25
MAX_RETRIES = 3
RETRY_BACKOFF = 3.0


# === API Setup ===
def load_api_key():
    dotenv_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
    load_dotenv(dotenv_path=dotenv_path)
    api_key = os.getenv("OPENAI_API_KEY") or SystemSettings.api_key
    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY not found.")
    return api_key


client = OpenAI(api_key=load_api_key())


# === Load CSVs ===
def load_scan_groups(path: str) -> list[str]:
    logger.info(f"Loading scan groups from: {path}")
    df = pd.read_csv(path)
    return df["scan_group"].dropna().tolist()


def load_scans_to_align(path: str) -> list[str]:
    logger.info(f"📥 Loading scan names from: {path}")
    df = pd.read_csv(path)
    scan_names = df["scan_name"].dropna().tolist()
    logger.info(f"✅ Loaded {len(scan_names)} scan names.")
    return scan_names

# === GPT Interaction ===
def get_proposed_matches(messages: list[dict]) -> dict:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("🔁 Sending batch to GPT...")
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content.strip()
            usage = response.usage
            token_usage = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }
            logger.info("✅ GPT response received.")
            return {
                "proposed_matches": json.loads(content).get("proposed_matches", []),
                "response_text": content,
                "token_usage": token_usage
            }
        except Exception as e:
            logger.error(f"❌ GPT call failed (attempt {attempt}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF * attempt)
    return {"proposed_matches": [], "response_text": "", "token_usage": {}}


# === Logging ===
def log_gpt_batch(batch_num: int, messages: list[dict], response_data: dict, script_name: str = "run_scan_group_alignment"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(LOG_BASE_DIR, exist_ok=True)
    log_path = os.path.join(LOG_BASE_DIR, f"{script_name}_batch{batch_num}_{timestamp}.json")

    log_data = {
        "timestamp": timestamp,
        "batch_number": batch_num,
        "prompt": messages,
        "gpt_response": response_data.get("response_text", ""),
        "token_usage": response_data.get("token_usage", {})
    }

    try:
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
        logger.info(f"📝 Saved GPT batch log: {log_path}")
    except Exception as e:
        logger.error(f"❌ Could not save GPT log: {e}")


# === Main ===
def main(scan_groups_path: str, mapping_csv_path: str, output_csv_path: str, prompt_path: str, max_batches: int = None):
    logger.info("🚀 Starting GPT scan group alignment...")

    scan_groups = load_scan_groups(scan_groups_path)
    all_scans = load_scans_to_align(mapping_csv_path)
    total_batches = len(all_scans) // BATCH_SIZE + int(len(all_scans) % BATCH_SIZE != 0)
    if max_batches:
        total_batches = min(total_batches, max_batches)

    logger.info(f"🔄 Processing {total_batches} batches of {BATCH_SIZE} scans each...\n")

    all_matches = []

    for batch_num in tqdm(range(1, total_batches + 1), desc="Aligning", unit="batch"):
        start = (batch_num - 1) * BATCH_SIZE
        end = start + BATCH_SIZE
        scan_batch = all_scans[start:end]

        print(f"\n📦 Batch {batch_num} — {len(scan_batch)} scans")

        messages = generate_scan_prompt(
            scan_batch,
            prompt_path=prompt_path,
            scan_group_csv=scan_groups_path
        )

        if not messages:
            logger.error(f"❌ Prompt generation failed for batch {batch_num}. Skipping.")
            continue
        
        gpt_result = get_proposed_matches(messages)
        log_gpt_batch(batch_num, messages, gpt_result)

        matches = gpt_result["proposed_matches"]
        print(f"✅ Received {len(matches)} matches")
        all_matches.extend(matches)

    logger.info("💾 Writing final aligned CSV...")
    apply_proposed_sg_to_csv(
        mapping_csv_path=mapping_csv_path,
        scan_groups_path=scan_groups_path,
        output_csv_path=output_csv_path,
        proposed_matches=all_matches,
        run_label="gpt-4o-mini"
    )
    logger.info(f"🎉 CSV written to: {output_csv_path}")


# === CLI ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GPT-based scan group alignment.")
    parser.add_argument("--scan-groups-path", type=str, default=DEFAULT_SCAN_GROUPS_PATH)
    parser.add_argument("--mapping-csv-path", type=str, default=DEFAULT_MAPPING_CSV_PATH)
    parser.add_argument("--output-csv-path", type=str, default=DEFAULT_OUTPUT_CSV_PATH)
    parser.add_argument("--prompt-path", type=str, default=DEFAULT_PROMPT_PATH)
    parser.add_argument("--max-batches", type=int, help="Limit how many batches to process.")
    args = parser.parse_args()

    main(
        scan_groups_path=args.scan_groups_path,
        mapping_csv_path=args.mapping_csv_path,
        output_csv_path=args.output_csv_path,
        prompt_path=args.prompt_path,
        max_batches=args.max_batches
    )
