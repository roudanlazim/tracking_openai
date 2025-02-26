import time
import openai
import json
from openai import OpenAIError
from modules.logging_utils import logger
from modules.system_settings import SystemSettings
from modules.prompt_generator import load_prompt  # ✅ Ensure AI uses JSON-based prompt

def get_openai_response(prompt, retries=3):
    """Send request to OpenAI API and return response, retrying on failure."""
    
    # ✅ Fetch API Key dynamically at runtime
    api_key = SystemSettings.api_key  
    if not api_key:
        logger.error("❌ No API key found in SystemSettings. Please enter it in `user_input.py`.")
        return "Error: No API Key", 0, 0

    # ✅ Ensure a model is set
    model = SystemSettings.model_name or "gpt-3.5-turbo"  # ✅ Set a default model if missing

    # ✅ Initialize OpenAI Client (Only if API key exists)
    client = openai.OpenAI(api_key=api_key)  

    for attempt in range(retries):
        try:
            logger.info(f"🚀 Attempt {attempt + 1}: Sending request to OpenAI with model `{model}`")
            logger.debug(f"📨 Full Prompt Sent to OpenAI:\n{prompt}")  # ✅ Debugging log

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a shipment tracking AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            predicted_status = response.choices[0].message.content.strip()
            token_input = response.usage.prompt_tokens
            token_output = response.usage.completion_tokens

            logger.info(f"✅ AI Response: {predicted_status}")
            logger.debug(f"📊 Tokens Used - Input: {token_input}, Output: {token_output}")

            return predicted_status, token_input, token_output

        except OpenAIError as e:  # ✅ Log OpenAI's Exact Error Message
            logger.error(f"❌ OpenAI API Error: {e}")
            wait_time = (attempt + 1) * 5  # Exponential backoff
            logger.warning(f"⚠️ Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    logger.error("❌ OpenAI API request failed after multiple attempts.")
    return "Error: API request failed", 0, 0

def get_ai_prediction(input_text, status_elements, prompt_file):
    """Processes input text using AI and retrieves the predicted status using a JSON-based prompt."""
    
    # ✅ Fetch API Key at runtime
    if not SystemSettings.api_key:
        logger.error("❌ No API Key Found! Please set your OpenAI API Key.")
        return "Error: No API Key", (0, 0)

    # ✅ Load JSON-based prompt
    prompt_data = load_prompt(prompt_file)
    if not prompt_data:
        logger.error(f"❌ Failed to load prompt file: {prompt_file}")
        return "Error: Failed to load prompt", (0, 0)

    # ✅ Debugging: Log Loaded Prompt Data
    logger.debug(f"📄 Loaded Prompt Data from {prompt_file}: {json.dumps(prompt_data, indent=2)}")

    # ✅ Build Prompt from JSON
    instruction = prompt_data.get("instruction", "Analyze shipment tracking data and return the correct status.")
    examples = prompt_data.get("examples", [])

    # ✅ FIX: Change "input" to "tracking_data"
    example_text = "\n".join([
        f"Tracking Data: {ex.get('tracking_data', 'MISSING TRACKING DATA')}\nOutput: {ex.get('output', 'MISSING OUTPUT')}"
        for ex in examples
    ])

    full_prompt = f"""
    **{instruction}**
    
    **Possible Statuses:**
    {', '.join(status_elements)}

    **Examples:**
    {example_text}

    **User Input:**
    {input_text}
    """

    # ✅ Call OpenAI
    ai_response, token_input, token_output = get_openai_response(full_prompt)

    # ✅ Log response
    logger.info(f"🔹 AI Model Prediction: {ai_response}")

    return ai_response, (token_input, token_output)