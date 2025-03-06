from modules.logging_utils import logger  # Import centralized logger
import os
import json

CONFIG_FILE = os.path.join("config", "settings.json")

def get_relative_path(settings, key, default_filename):
    """Ensure paths are relative, falling back to defaults."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(base_dir, "config", default_filename)
    return settings.get(key, default_path)

def load_settings():
    """Load settings directly from `settings.json`."""
    if not os.path.exists(CONFIG_FILE):
        logger.warning("⚠️ No `settings.json` found in `config/`. Using defaults.")
        return {}

    try:
        with open(CONFIG_FILE, "r") as f:
            settings = json.load(f)
        logger.info("✅ Settings loaded successfully.")
        return settings
    except Exception as e:
        logger.error(f"❌ Error loading `settings.json`: {str(e)}")
        return {}

# Assign SETTINGS once after function definition
SETTINGS = load_settings()