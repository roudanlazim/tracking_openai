from modules.prompt_generator import generate_prompt
from modules.json_handler import load_json

# Load prompt
selected_prompt_file = "data/prompts/system_prompt.json"
system_prompt_json = load_json(selected_prompt_file)

# Mock shipment data
shipments = [
    {
        "tracking_number": "123456",
        "shipment_id": "A1B2C3",
        "carrier": "DHL",
        "scans": [
            {"timestamp": "2024-03-17T10:00:00", "scan": "Collected"},
            {"timestamp": "2024-03-17T12:00:00", "scan": "In Transit"}
        ]
    }
]

messages = generate_prompt(shipments, selected_prompt_file)
print(messages)
