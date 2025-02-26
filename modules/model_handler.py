import openai
from modules.logging_utils import logger
from modules.system_settings import SystemSettings

def fetch_openai_models():
    """Retrieve the list of available OpenAI models from the API."""
    
    if SystemSettings.model_type != "openai":
        logger.warning("⚠️ OpenAI models requested, but OpenAI is not selected. Returning default model.")
        return ["gpt-3.5-turbo"]

    if not SystemSettings.api_key:
        logger.error("❌ API key is missing but should have been set! Aborting.")
        return ["gpt-3.5-turbo"]

    try:
        client = openai.OpenAI(api_key=SystemSettings.api_key)
        models = client.models.list()

        # Extract model names and filter relevant ones
        available_models = [model.id for model in models.data if "gpt" in model.id]
        if not available_models:
            logger.warning("⚠️ No OpenAI models retrieved. Defaulting to 'gpt-3.5-turbo'.")
            return ["gpt-3.5-turbo"]

        logger.info(f"✅ Retrieved {len(available_models)} OpenAI models.")
        return available_models

    except openai.OpenAIError as e:
        logger.error(f"❌ Error fetching OpenAI models: {str(e)}")
        return ["gpt-3.5-turbo"]