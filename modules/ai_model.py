import time
import openai
from modules.logging_utils import logger
from modules.system_settings import SystemSettings

def get_openai_response(prompt, retries=3):
    """Send request to OpenAI API and return response, retrying on failure."""
    
    api_key = SystemSettings.api_key
    model = SystemSettings.model_name  

    if not api_key:
        logger.error("❌ No API key provided. Please set an API key in SystemSettings.")
        return "Error: No API key", 0, 0

    client = openai.OpenAI(api_key=api_key) if hasattr(openai, "OpenAI") else openai  # ✅ Fix OpenAI constructor

    for attempt in range(retries):
        try:
            logger.debug(f"🚀 Sending request to OpenAI API (Attempt {attempt + 1})...")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": "You are an assistant."},
                          {"role": "user", "content": prompt}],
                temperature=0
            )

            predicted_status = response.choices[0].message.content.strip()
            token_input = response.usage.prompt_tokens
            token_output = response.usage.completion_tokens

            logger.info(f"✅ AI Response: {predicted_status}")
            logger.debug(f"📊 Tokens Used - Input: {token_input}, Output: {token_output}")

            return predicted_status, token_input, token_output

        except openai.error.RateLimitError as e:
            wait_time = (attempt + 1) * 5  # Exponential backoff
            logger.warning(f"⚠️ OpenAI Rate Limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    logger.error("❌ OpenAI API request failed after multiple attempts.")
    return "Error: API request failed", 0, 0