import sys
import os

# ✅ Add project root to `sys.path` so Python can find `modules/`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from modules.user_input import (
    get_model_type, get_model_name, get_api_key,
    select_csv_file, select_csv_column, select_prompt, confirm_selection
)
from modules.system_settings import SystemSettings

print("\n🧠 Testing get_model_type()")
get_model_type()
print(f"Selected Model Type: {SystemSettings.model_type}")

print("\n🤖 Testing get_model_name()")
get_model_name()
print(f"Selected Model Name: {SystemSettings.model_name}")

print("\n🔑 Testing get_api_key()")
get_api_key()
print(f"Stored API Key: {SystemSettings.api_key}")

print("\n📂 Testing select_csv_file()")
csv_file = select_csv_file()
print(f"Selected CSV File: {csv_file}")

print("\n📊 Testing select_csv_column()")
selected_column = select_csv_column()
print(f"Selected Column: {selected_column}")

print("\n📄 Testing select_prompt()")
prompt_file = select_prompt()
print(f"Selected Prompt File: {prompt_file}")

print("\n⚠️ Testing confirm_selection()")
if confirm_selection():
    print("✅ User confirmed selections.")
else:
    print("🚫 User canceled selections.")