# duckdns_updater.py

import requests
from datetime import datetime
import os

# Replace with your DuckDNS subdomain and token
DOMAIN = "openai-pvr-metabase.duckdns.org"
TOKEN = "f155c10c-f14f-4ea7-b5c8-a6ce168cf75f"
UPDATE_URL = f"https://www.duckdns.org/update?domains={DOMAIN}&token={TOKEN}&ip="

# Update request
try:
    response = requests.get(UPDATE_URL)
    result = response.text.strip()

    # Logging
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} - {result}\n"
    with open(os.path.join(os.path.dirname(__file__), "duckdns.log"), "a") as log_file:
        log_file.write(log_line)

    print(log_line, end='')

except Exception as e:
    print(f"Failed to update DuckDNS: {e}")
