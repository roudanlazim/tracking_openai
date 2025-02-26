from modules.logging_utils import logger  # ✅ Import centralized logger
import os
import json
import datetime
from modules.file_handler import load_json, save_json, list_files

PROMPT_DIR = "data/prompts/"

# ✅ Ensure prompt directory exists
os.makedirs(PROMPT_DIR, exist_ok=True)

### ✅ LIST, LOAD, SAVE PROMPTS
def list_prompt_files():
    """List available prompt JSON files in `data/prompts/`."""
    try:
        prompt_files = list_files(PROMPT_DIR, ".json")  # ✅ Uses file_handler function
        logger.info(f"✅ Found {len(prompt_files)} available prompts.")
        return prompt_files
    except Exception as e:
        logger.error(f"❌ Error listing prompt files: {str(e)}")
        return []

def load_prompt(prompt_file):
    """Load prompt template from a JSON file."""
    prompt_path = os.path.join(PROMPT_DIR, prompt_file)  # ✅ Convert filename to full path
    
    if not os.path.exists(prompt_path):
        logger.error(f"❌ Prompt file not found: {prompt_path}")
        return None

    return load_json(prompt_path)  # ✅ Load full path

def save_prompt(prompt_file, prompt_data):
    """Save a new or modified prompt JSON file."""
    prompt_path = os.path.join(PROMPT_DIR, prompt_file)  # ✅ Convert filename to full path
    
    # ✅ Prevent accidental overwriting
    if os.path.exists(prompt_path):
        confirm = input(f"⚠️ Prompt '{prompt_file}' already exists. Overwrite? (yes/no): ").strip().lower()
        if confirm != "yes":
            logger.info("❌ Prompt save cancelled by user.")
            return None

    save_json(prompt_path, prompt_data)  # ✅ Now using file_handler
    logger.info(f"✅ Saved prompt: {prompt_path}")
    return prompt_path

def generate_prompt(prompt_file, scan_history, status_elements):
    """Generate a structured AI prompt based on full shipment scan history and status elements."""
    prompt_template = load_prompt(prompt_file)
    
    if not prompt_template:
        logger.error(f"❌ Failed to load prompt file: {prompt_file}")
        return ""

    instruction = prompt_template.get("instruction", "Analyze the shipping data and return the correct status.")
    rules = "\n".join(prompt_template.get("rules", []))
    status_list = ", ".join(status_elements)

    # ✅ Format Scan History for AI (Show Most Recent Events First)
    scan_events = scan_history.split(",")  # ✅ Split shipment scans
    formatted_scan_history = "\n".join([f"- {event.strip()}" for event in scan_events[-10:]])  # ✅ Show Last 10 Events

    structured_prompt = f"""
    **{instruction}**
    
    **Rules:**
    {rules}

    **Possible Statuses:**
    {status_list}

    **Shipment Tracking History (Most Recent First):**
    {formatted_scan_history}
    """

    logger.debug(f"✅ Generated AI Prompt:\n{structured_prompt}")
    return structured_prompt

### ✅ SELECT OR CREATE A PROMPT (Moved from `user_input.py`)
def select_or_create_prompt():
    """Allow user to select an existing prompt or create a new one."""
    os.makedirs(PROMPT_DIR, exist_ok=True)
    prompt_files = list_prompt_files()

    print("\n💡 Prompt Selection")
    print("1 - Select an existing prompt")
    print("2 - Create a new prompt")

    choice = input("Choose an option (1-2): ").strip()

    if choice == "1":
        return select_json_prompt()
    elif choice == "2":
        return create_new_prompt()
    
    print("❌ Invalid choice. Returning default prompt.")
    return select_json_prompt()

def select_json_prompt():
    """Allow user to select an existing JSON prompt file from `data/prompts/`."""
    prompt_files = list_prompt_files()
    if not prompt_files:
        logger.error("❌ No JSON prompt files found in `data/prompts/`. Exiting.")
        exit(1)

    print("\n📂 Available JSON Prompt Files:")
    for idx, file in enumerate(prompt_files, start=1):
        print(f"{idx} - {file}")

    while True:
        choice = input("\nSelect a JSON prompt (Enter number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(prompt_files):
            selected_prompt = os.path.join(PROMPT_DIR, prompt_files[int(choice) - 1])
            logger.info(f"✅ Selected JSON prompt: {selected_prompt}")
            return selected_prompt
        else:
            print("❌ Invalid choice. Please enter a valid number.")

def create_new_prompt():
    """Allow user to create a new prompt and save it as JSON."""
    print("\n📝 Creating a New Prompt")
    default_prompt = {
        "instruction": "Analyze the shipping journey and return the most appropriate status.",
        "examples": [
            {"input": "Shipment scanned at warehouse", "output": "In Transit"},
            {"input": "Package delivered to recipient", "output": "Delivered"}
        ]
    }

    print("\n📌 Default Prompt JSON:")
    print(json.dumps(default_prompt, indent=2))

    edit_choice = input("\nDo you want to edit this prompt? (yes/no): ").strip().lower()
    if edit_choice == "yes":
        default_prompt["instruction"] = input("Enter new instruction: ").strip()
    
    new_prompt_filename = f"prompt_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    new_prompt_path = os.path.join(PROMPT_DIR, new_prompt_filename)

    save_json(new_prompt_path, default_prompt)  # ✅ Save using `file_handler.py`

    logger.info(f"✅ New prompt saved as {new_prompt_path}")
    return new_prompt_filename