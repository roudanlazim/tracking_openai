from modules.logging_utils import logger  # ✅ Import centralized logger
import json
import os
from modules.file_handler import load_json, save_json, get_json_path

CONFIG_FILE = "settings.json"
CACHED_JSON_DATA = {}  # Store JSON data in memory

def get_relative_path(settings, key, default_filename):
    """Ensure paths are relative, falling back to defaults."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(base_dir, "config", default_filename)

    return settings.get(key, default_path)

def load_settings():
    """Load settings from JSON file, prompting user for missing paths."""
    
    settings = load_json(CONFIG_FILE, fallback={})
    
    if not settings:
        logger.warning("⚠️ No existing settings found, using defaults.")

    # Convert paths to relative using settings dictionary (not SETTINGS)
    settings["status_elements_file"] = get_relative_path(settings, "status_elements_file", "status_elements.json")

    CACHED_JSON_DATA["status_elements"] = load_json(settings["status_elements_file"], fallback={"statuses": ["Delivered", "In Transit", "Returned to Sender"]})

    save_json(CONFIG_FILE, settings)
    logger.info("✅ Settings loaded successfully.")

    return settings

# ✅ Assign SETTINGS after the function is fully defined
SETTINGS = load_settings()
