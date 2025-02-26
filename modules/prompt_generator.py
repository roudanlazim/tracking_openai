from modules.logging_utils import logger  # ✅ Import centralized logger
import os
from modules.file_handler import load_json, save_json  # ✅ Now using file_handler for both loading & saving

PROMPT_DIR = "data/prompts/"

# ✅ Ensure prompt directory exists
os.makedirs(PROMPT_DIR, exist_ok=True)

def list_prompt_files():
    """List available prompt JSON files in `data/prompts/`."""
    try:
        prompt_files = [f for f in os.listdir(PROMPT_DIR) if f.endswith(".json")]
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

def generate_prompt(prompt_file):
    """Generate a structured AI prompt based on a selected JSON prompt file."""
    prompt_path = os.path.join(PROMPT_DIR, prompt_file)  # ✅ Convert filename to full path
    
    try:
        prompt_template = load_json(prompt_path)  # ✅ Load full path
        
        if not prompt_template:
            logger.error(f"❌ Failed to load prompt file: {prompt_path}")
            return ""

        # ✅ Fully dynamic prompt structure
        prompt_sections = []
        
        for key, value in prompt_template.items():
            if isinstance(value, list):  
                section_text = "\n".join([f"- {item}" if isinstance(item, str) else f"Input: {item['input']}\nOutput: {item['output']}" for item in value])
            else:
                section_text = str(value)

            prompt_sections.append(f"\n**{key.replace('_', ' ').title()}**:\n{section_text}")

        final_prompt = "\n".join(prompt_sections)

        logger.debug(f"✅ Generated AI prompt from {prompt_file} successfully.")
        return final_prompt

    except Exception as e:
        logger.error(f"❌ Error generating prompt: {str(e)}")
        return ""