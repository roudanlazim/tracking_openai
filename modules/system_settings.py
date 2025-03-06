import os
import json
from modules.logging_utils import logger
from config.settings_loader import load_settings # ✅ Ensure correct function is used

class SystemSettings:
    """Stores user selections during runtime for AI prediction."""
    
    # Load settings dynamically
    settings = load_settings()

    model_type = settings.get("model_type", None)
    model_name = settings.get("model_name", None)
    api_key = settings.get("api_key", None)
    input_file = settings.get("input_file", None)
    selected_column = settings.get("selected_column", None)
    prompt_file = settings.get("prompt_file", None)

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
        logger.info("🔄 System settings reset.")
