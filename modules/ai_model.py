import time
import openai
from openai import OpenAIError
from modules.logging_utils import logger
from modules.system_settings import SystemSettings

# ✅ Initialize global MODEL_CACHE to avoid NameError
MODEL_CACHE = None  

def get_openai_response(prompt_messages, retries=3):
    """Send request to OpenAI API and return response, retrying on failure."""
    
    # ✅ Ensure correct API Key is set
    api_key = SystemSettings.api_key  
    if not api_key:
        logger.error("❌ No API key found. Please enter it in `user_input.py`.")
        return "Error: No API Key", 0, 0

    # ✅ Default to GPT-4o Mini if no model is explicitly selected
    model = SystemSettings.model_name if SystemSettings.model_name else "gpt-4o-mini"
    
    client = openai.OpenAI(api_key=api_key)

    for attempt in range(retries):
        try:
            logger.info(f"🚀 Attempt {attempt + 1}: Sending request to OpenAI...")

            # ✅ Send structured prompt to OpenAI
            response = client.chat.completions.create(
                model=model,
                messages=prompt_messages,
                temperature=0
            )

            predicted_status = response.choices[0].message.content.strip()
            token_input = response.usage.prompt_tokens
            token_output = response.usage.completion_tokens

            logger.info(f"✅ AI Response: {predicted_status}")
            return predicted_status, token_input, token_output

        except openai.OpenAIError as e:
            logger.error(f"❌ OpenAI API Error: {e}")
            wait_time = (attempt + 1) * 5  # Exponential backoff
            logger.warning(f"⚠️ Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    logger.error("❌ OpenAI API request failed after multiple attempts.")
    return "Error: API request failed", 0, 0

def fetch_openai_models():
    """Retrieve the list of available OpenAI models from the API, caching the result."""
    global MODEL_CACHE

    # ✅ Return cached models if already retrieved
    if MODEL_CACHE is not None:
        return MODEL_CACHE

    if SystemSettings.model_type != "openai":
        logger.warning("⚠️ OpenAI models requested, but OpenAI is not selected. Returning default model.")
        return ["gpt-4o-mini"]

    if not SystemSettings.api_key:
        logger.error("❌ API key is missing but should have been set! Aborting.")
        return ["gpt-4o-mini"]

    try:
        client = openai.OpenAI(api_key=SystemSettings.api_key)
        models = client.models.list()

        # Extract model names and filter relevant ones
        MODEL_CACHE = [model.id for model in models.data if "gpt" in model.id]

        if not MODEL_CACHE:
            logger.warning("⚠️ No OpenAI models retrieved. Defaulting to 'gpt-4o-mini'.")
            return ["gpt-4o-mini"]

        logger.info(f"✅ Retrieved {len(MODEL_CACHE)} OpenAI models.")
        return MODEL_CACHE

    except openai.OpenAIError as e:
        logger.error(f"❌ Error fetching OpenAI models: {str(e)}")
        return ["gpt-4o-mini"]