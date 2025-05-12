import os
import json
import pandas as pd
from modules.json_handler import load_json
from modules.logging_utils import logger

PROMPT_DIR = "data/prompts"
os.makedirs(PROMPT_DIR, exist_ok=True)

def load_prompt_from_json(prompt_file: str) -> str:
    """
    Load system prompt as a single string from a structured JSON file.
    This file should contain a "content" field, which is either a string or a list of strings.
    """
    if not os.path.exists(prompt_file):
        logger.error(f"🚨 Prompt file NOT found: {prompt_file}")
        return ""

    prompt_data = load_json(prompt_file)
    if not prompt_data or "content" not in prompt_data:
        logger.error(f"🚨 Invalid or missing 'content' in prompt JSON: {prompt_file}")
        return ""

    content = prompt_data["content"]
    if isinstance(content, list):
        return "\n".join(content)
    elif isinstance(content, str):
        return content
    else:
        logger.error(f"🚨 Unexpected format for 'content' in {prompt_file}")
        return ""

def generate_scan_prompt(scan_batch, prompt_path, scan_group_csv="data/scan-groups.csv"):
    """
    Generates a structured OpenAI prompt from a JSON template and scan group CSV.

    Args:
        scan_batch (list): A list of raw scan messages (strings).
        prompt_path (str): Path to the JSON prompt template.
        scan_group_csv (str): Path to the scan-groups.csv file.

    Returns:
        list: A list of two dicts formatted for OpenAI API (system + user).
    """
    # ✅ Load the prompt template
    prompt_json = load_json(prompt_path)
    if not prompt_json:
        logger.error(f"❌ Failed to load prompt JSON: {prompt_path}")
        return None

    # ✅ Load scan group names from CSV
    try:
        df = pd.read_csv(scan_group_csv)
        if "scan_group" not in df.columns:
            logger.error("❌ CSV missing 'scan_group' column.")
            return None
        scan_group_list = df["scan_group"].dropna().tolist()
        formatted_sg_text = "\n".join([f"- {sg}" for sg in scan_group_list])
    except Exception as e:
        logger.error(f"❌ Failed to load scan groups from CSV: {e}")
        return None

    # ✅ Build system message by replacing placeholder
    system_content = "\n".join(prompt_json.get("content", []))
    if "<<scan_groups>>" not in system_content:
        logger.warning("⚠️ No <<scan_groups>> placeholder found in prompt template.")
    system_content = system_content.replace("<<scan_groups>>", formatted_sg_text)

    # ✅ Format user message from scan batch
    user_content = json.dumps({"scans_to_classify": scan_batch}, indent=2)

    # ✅ Return prompt messages
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]