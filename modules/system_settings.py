from modules.logging_utils import logger

class SystemSettings:
    """Stores user selections during runtime for AI prediction."""

    model_type = None   # e.g., OpenAI
    model_name = None   # e.g., gpt-4
    api_key = None      # API key (not stored permanently)
    input_file = None   # Selected CSV file
    selected_column = None  # Column to predict from
    prompt_file = None  # Selected JSON prompt file

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