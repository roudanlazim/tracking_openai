from modules.logging_utils import logger

class SystemSettings:
    """Holds global settings for the AI prediction system."""
    
    model_type = None  # LLM model type (e.g., OpenAI, Anthropic)
    model_name = None  # Selected AI model name
    api_key = None  # API key (Stored only during runtime)
    prediction_column = "ScanGroups"  # Default CSV column for predictions

    @classmethod
    def set_api_key(cls, key):
        """Set the API key securely for the session."""
        cls.api_key = key
        logger.info("✅ API key set successfully (not logged for security).")

    @classmethod
    def log_settings(cls):
        """Log current system settings."""
        logger.info(f"🔧 System Settings - Model Type: {cls.model_type}, Model Name: {cls.model_name}, Prediction Column: {cls.prediction_column}")

# ✅ Log settings when the module is first loaded
logger.info("✅ System settings initialized.")
SystemSettings.log_settings()
