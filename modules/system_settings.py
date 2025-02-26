import os
import json
from modules.logging_utils import logger
from modules.file_handler import load_json  # ✅ Ensure correct function is used

class SystemSettings:
    """Stores user selections during runtime for AI prediction."""

    model_type = None
    model_name = None
    api_key = None
    input_file = None
    selected_column = None
    prompt_file = None
    status_elements = None  # ✅ Ensure this is initialized properly

    @classmethod
    def log_settings(cls):
        """Log the current system settings for debugging."""
        logger.info(f"🔧 System Settings Updated - Model: {cls.model_name}, "
                    f"CSV: {cls.input_file}, Column: {cls.selected_column}, Prompt: {cls.prompt_file}")

    @classmethod
    def reset(cls):
        """Reset all cached settings (if needed)."""
        cls.model_type = None
        cls.model_name = None
        cls.api_key = None
        cls.input_file = None
        cls.selected_column = None
        cls.prompt_file = None
        cls.status_elements = None  # ✅ Reset status elements
        logger.info("🔄 System settings reset.")

    @classmethod
    def load_status_elements(cls, status_file="data/status_elements.json"):
        """Load status elements dynamically from JSON file."""
        if not os.path.exists(status_file):
            logger.error(f"❌ Status elements file missing: {status_file}. Using default statuses.")
            cls.status_elements = ["Delivered", "In Transit", "Returned to Sender"]  # ✅ Ensure it’s a list
            return

        cls.status_elements = load_json(status_file)

        # ✅ Fix: Ensure `status_elements` is a **list**, not a dictionary
        if not isinstance(cls.status_elements, list):
            logger.warning("⚠️ Status elements file is invalid format. Using default values.")
            cls.status_elements = ["Delivered", "In Transit", "Returned to Sender"]

        logger.info(f"✅ Status elements loaded successfully: {cls.status_elements}")

    @classmethod
    def set_status_elements(cls, elements):
        """Manually set status elements if needed."""
        cls.status_elements = elements
        logger.info(f"✅ Manually updated status elements: {elements}")