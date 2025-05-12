import os
import json
import pandas as pd
import unicodedata
from modules.json_handler import load_json
from modules.logging_utils import logger

PROMPT_DIR = "data/prompts"
os.makedirs(PROMPT_DIR, exist_ok=True)

def normalize_smart_punctuation(text: str) -> str:
    """
    Replace broken UTF-8 characters (e.g., Â–, â€“) with safe equivalents.
    Keep content meaning intact while ensuring all characters are valid.
    """
    replacements = {
        # Quotes
        "“": '"', "”": '"', "‘": "'", "’": "'",
        # Dashes and ellipsis
        "–": "-", "—": "-", "…": "...",
        # Windows encoding artifacts
        "Â–": "-", "â€“": "-", "â€”": "-", "â€•": "-", "â€”": "-",
        "Ã©": "é", "Ã¼": "ü", "Ã": "a",
        # Odd invisible characters
        "\u0096": "-", "\u0092": "'", "\u0093": '"', "\u0094": '"',
        "\xa0": " ", "\u00a0": " ",
        "\u2026": "...", "\u200b": "",  # ellipsis, zero-width space
    }

    # Step 1: Replace known bad sequences
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Step 2: Normalize and remove control characters (C0 and C1)
    text = unicodedata.normalize("NFKC", text)
    text = ''.join(ch for ch in text if unicodedata.category(ch)[0] != "C")

    return text.strip()

def clean_scan_text(text: str) -> str:
    return normalize_smart_punctuation(text)


def load_prompt_from_json(prompt_file: str) -> str:
    """
    Load system prompt from structured JSON containing a 'content' field.
    Handles both string or list formats. Applies deep cleaning.
    """
    if not os.path.exists(prompt_file):
        logger.error(f"🚨 Prompt file NOT found: {prompt_file}")
        return ""

    try:
        prompt_data = load_json(prompt_file)
    except Exception as e:
        logger.error(f"🚨 Failed to parse JSON: {e}")
        return ""

    if not prompt_data or "content" not in prompt_data:
        logger.error(f"🚨 Invalid or missing 'content' in prompt JSON: {prompt_file}")
        return ""

    content = prompt_data["content"]
    if isinstance(content, list):
        combined = "\n".join(content)
    elif isinstance(content, str):
        combined = content
    else:
        logger.error(f"🚨 Unexpected format for 'content' in {prompt_file}")
        return ""

    return normalize_smart_punctuation(combined)


def generate_scan_prompt(scan_batch, prompt_path, scan_group_csv="data/scan-groups.csv"):
    """
    Generate structured OpenAI prompt using system JSON and scan groups CSV.

    Args:
        scan_batch (list): Raw scan messages.
        prompt_path (str): Path to system prompt JSON file.
        scan_group_csv (str): Path to scan group list CSV.

    Returns:
        list: [system_message, user_message] for OpenAI API.
    """
    # ✅ Load and clean system prompt
    raw_prompt = load_prompt_from_json(prompt_path)
    if not raw_prompt:
        logger.error(f"❌ Failed to load or clean system prompt: {prompt_path}")
        return None

    # ✅ Load and clean scan group names
    try:
        df = pd.read_csv(scan_group_csv)
        if "scan_group" not in df.columns:
            logger.error("❌ CSV missing 'scan_group' column.")
            return None
        scan_group_list = df["scan_group"].dropna().tolist()
        formatted_sg_text = "\n".join(f"- {normalize_smart_punctuation(sg)}" for sg in scan_group_list)
    except Exception as e:
        logger.error(f"❌ Failed to load scan groups from CSV: {e}")
        return None

    # ✅ Insert into system prompt
    if "<<scan_groups>>" in raw_prompt:
        system_content = raw_prompt.replace("<<scan_groups>>", formatted_sg_text)
    else:
        logger.warning("⚠️ No <<scan_groups>> placeholder found in prompt template.")
        system_content = raw_prompt

    # ✅ Normalize scans
    cleaned_batch = [clean_scan_text(scan) for scan in scan_batch]
    user_content = json.dumps({"scans_to_classify": cleaned_batch}, indent=2)

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]