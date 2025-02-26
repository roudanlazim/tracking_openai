import sys
import os

# ✅ Add project root to `sys.path` so Python can find `modules/`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from modules.prompt_generator import (
    list_prompt_files, select_or_create_prompt, create_new_prompt, load_prompt, generate_prompt
)

print("\n📂 Testing list_prompt_files()")
print(list_prompt_files())

print("\n📝 Testing select_or_create_prompt()")
print(select_or_create_prompt())

print("\n✅ Testing create_new_prompt()")
print(create_new_prompt())

print("\n📄 Testing load_prompt()")
print(load_prompt("test_prompt.json"))  # Change filename if needed

print("\n🚀 Testing generate_prompt()")
print(generate_prompt("test_prompt.json"))  # Change filename if needed