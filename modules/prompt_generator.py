import os
import json
from modules.json_handler import load_json
from modules.logging_utils import logger

# You may still keep a PROMPT_DIR if you want to create it, 
# but we won't forcibly prepend it to 'prompt_file'.
PROMPT_DIR = "data/prompts"
os.makedirs(PROMPT_DIR, exist_ok=True)

def load_prompt(prompt_file):
    """Load system prompt from JSON."""
    prompt_path = prompt_file  
    if not os.path.exists(prompt_path):
        logger.error(f"🚨 Prompt file NOT found: {prompt_path}")
        print(f"🚨 Prompt file NOT found: {prompt_path}")  # Debug print
        return None

    prompt_data = load_json(prompt_path)
    if not prompt_data:
        logger.error(f"🚨 Failed to load JSON: {prompt_path}")
        print(f"🚨 Failed to load JSON: {prompt_path}")  # Debug print
        return None

    return prompt_data

def generate_prompt(shipments, prompt_file):
    """
    Generates the full structured prompt from the JSON file
    plus the shipments data. 
    """
    system_prompt = load_prompt(prompt_file)
    if not system_prompt:
        logger.error(f"Failed to load system prompt: {prompt_file}")
        return None

    # "content" must be a list of strings in your JSON
    system_content = "\n".join(system_prompt["content"])

    shipment_details = []
    for shipment in shipments:
        scans_text = "\n".join(
            [f"- {scan['timestamp']}: {scan['scan']}" for scan in shipment["scans"]]
        )
        shipment_details.append(
            "\nShipment Start\n"
            f"Tracking Number: {shipment['tracking_number']}\n"
            f"Shipment ID: {shipment['shipment_id']}\n"
            f"Carrier: {shipment['carrier']}\n"
            "Scans:\n" + scans_text + "\n"
            "Shipment End\n"
        )

    final_prompt = [
        {"role": "developer", "content": system_content},
        {"role": "user", "content": "\n\n".join(shipment_details)}
    ]

    return final_prompt
