import sys
import os
import getpass  # ✅ Secure API key input

# ✅ Add project root to `sys.path` so Python can find `modules/`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from modules.token_counter import count_tokens
from modules.system_settings import SystemSettings

# ✅ Step 1: Collect API Key if not already set
if not SystemSettings.api_key:
    SystemSettings.api_key = getpass.getpass("\n🔑 Enter your OpenAI API Key: ").strip()

if not SystemSettings.api_key:
    print("❌ No API Key entered. Exiting test.")
    sys.exit(1)

print(f"✅ API Key Stored: {SystemSettings.api_key[:6]}********")  # ✅ Masked for security

# ✅ Step 2: Define test inputs for token counting
test_cases = [
    ("Hello world!", "Short sentence"),
    ("This is a longer sentence to test token counting accuracy.", "Longer sentence"),
    ("Shipment scanned at facility and out for delivery.", "Shipment update"),
    ("Your package was delivered to your front door at 2:45 PM.", "Delivery confirmation"),
    ("Multiple scans detected: Warehouse -> Transit -> Out for delivery -> Delivered.", "Detailed shipment scan history")
]

print("\n🚀 Running Token Counting Test...\n")

# ✅ Step 3: Run token counting test
for text, description in test_cases:
    token_count = count_tokens(text)
    print(f"🔹 {description}: {token_count} tokens")

print("\n✅ Token counting test completed.")