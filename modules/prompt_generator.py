import os
import json
from modules.logging_utils import logger
from modules.file_handler import list_files  
from modules.json_handler import load_json

PROMPT_DIR = "data/prompts/"

# ✅ Ensure prompt directory exists
os.makedirs(PROMPT_DIR, exist_ok=True)

def load_prompt(prompt_file):
    """Load system prompt from JSON."""
    prompt_path = os.path.join(PROMPT_DIR, prompt_file)  

    if not os.path.exists(prompt_path):
        logger.error(f"❌ Prompt file not found: {prompt_path}")
        return None

    return load_json(prompt_path)  

def generate_prompt(scan_history, prompt_file):
    """Generate the final structured prompt for AI processing."""
    system_prompt = load_prompt(prompt_file)
    
    if not system_prompt:
        logger.error(f"❌ Failed to load system prompt: {prompt_file}")
        return None

    return [
        {"role": "system", "content": system_prompt},  # ✅ System-level instruction
        {"role": "user", "content": scan_history}  # ✅ User shipment scan history
    ]