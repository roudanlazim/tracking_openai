import sys
import os
import getpass  # ✅ Hide API key input

# ✅ Add project root to `sys.path` so Python can find `modules/`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from modules.ai_model import get_ai_prediction
from modules.system_settings import SystemSettings
from modules.prompt_generator import load_prompt  # ✅ Ensure we load a prompt from JSON

# ✅ Step 1: Ask for API Key (Hidden Input) & Store It
if not SystemSettings.api_key:
    SystemSettings.api_key = getpass.getpass("\n🔑 Enter your OpenAI API Key: ").strip()

if not SystemSettings.api_key:
    print("❌ No API Key entered. Exiting test.")
    sys.exit(1)

print(f"✅ API Key Stored: {SystemSettings.api_key[:6]}********")  # ✅ Masked API key for security

# ✅ Step 2: Define Test Input
test_input_text = "Package delivered to customer"
test_status_elements = ["In Transit", "Delivered", "Exception"]

# ✅ Convert the prompt file path to an absolute path
test_prompt_file = os.path.abspath("data/prompts/example_prompt.json")

# ✅ Debugging: Print the absolute path to confirm location
print(f"🔍 Checking prompt file at: {test_prompt_file}")

# ✅ Step 3: Load JSON Prompt
prompt_data = load_prompt(test_prompt_file)
if not prompt_data:
    print(f"❌ Failed to load prompt file: {test_prompt_file}")
    sys.exit(1)

print(f"✅ Loaded Prompt from {test_prompt_file}")

### ✅ STEP 4: CALL AI MODEL
print("\n🤖 Testing get_ai_prediction()")
ai_response, token_counts = get_ai_prediction(test_input_text, test_status_elements, test_prompt_file)

### ✅ STEP 5: DISPLAY RESULTS
print(f"\n✅ AI Response: {ai_response}")
print(f"🔢 Token Counts: {token_counts}")

# ✅ Check if AI returned a valid response
if not ai_response or "error" in ai_response.lower():
    print("❌ AI returned an error! Check API key and model settings.")
else:
    print("✅ AI model call was successful!")
