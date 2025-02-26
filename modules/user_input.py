import os
import json
import datetime
from modules.logging_utils import logger
from modules.system_settings import SystemSettings
from modules.file_handler import load_json, save_json, load_csv  # ✅ Added save_json
from modules.model_handler import fetch_openai_models  # ✅ Handles OpenAI model selection

DATA_DIR = "data/"
PROMPT_DIR = "data/prompts/"

def select_or_create_prompt():
    """Allow user to select an existing prompt or create a new one."""
    os.makedirs(PROMPT_DIR, exist_ok=True)
    prompt_files = [f for f in os.listdir(PROMPT_DIR) if f.endswith(".json")]

    print("\n💡 Prompt Selection")
    print("1 - Select an existing prompt")
    print("2 - Create a new prompt")

    choice = input("Choose an option (1-2): ").strip()

    if choice == "1":
        if not prompt_files:
            print("⚠️ No existing prompts found. Creating a new one instead.")
            return create_new_prompt()

        print("\n📂 Available Prompts:")
        for idx, file in enumerate(prompt_files, start=1):
            print(f"{idx} - {file}")

        while True:
            prompt_choice = input("\nSelect a prompt (Enter number): ").strip()
            if prompt_choice.isdigit() and 1 <= int(prompt_choice) <= len(prompt_files):
                selected_prompt = os.path.join(PROMPT_DIR, prompt_files[int(prompt_choice) - 1])
                logger.info(f"✅ Selected prompt: {selected_prompt}")
                return selected_prompt
            else:
                print("❌ Invalid choice. Please enter a valid number.")

    elif choice == "2":
        return create_new_prompt()
    
    print("❌ Invalid choice. Returning default prompt.")
    return create_new_prompt()

def create_new_prompt():
    """Allow user to create a new prompt."""
    print("\n📝 Creating a New Prompt")
    default_prompt = {
        "instruction": "Analyze the shipping journey and return the most appropriate status.",
        "examples": [
            {"input": "Shipment scanned at warehouse", "output": "In Transit"},
            {"input": "Package delivered to recipient", "output": "Delivered"}
        ]
    }

    print("\n📌 Default Prompt JSON:")
    print(json.dumps(default_prompt, indent=2))

    edit_choice = input("\nDo you want to edit this prompt? (yes/no): ").strip().lower()
    if edit_choice == "yes":
        default_prompt["instruction"] = input("Enter new instruction: ").strip()
    
    new_prompt_filename = f"prompt_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    new_prompt_path = os.path.join(PROMPT_DIR, new_prompt_filename)

    save_json(new_prompt_path, default_prompt)  # ✅ Now using file_handler

    logger.info(f"✅ New prompt saved as {new_prompt_path}")
    return new_prompt_filename

def list_files(directory, extension):
    """List all files with a given extension in a directory."""
    return [f for f in os.listdir(directory) if f.endswith(extension)]

def get_model_type():
    """Asks the user for the model type and ensures API key is requested if needed."""
    print("🧠 Model Selection")
    print("1 - OpenAI GPT")
    print("2 - Other models (Coming soon)")
    
    choice = input("Select model type (1-2): ").strip()
    
    if choice == "1":
        SystemSettings.model_type = "openai"
        logger.info("✅ Model type set to OpenAI GPT")
        get_api_key()  # ✅ Ask for API key immediately after selecting OpenAI
    else:
        logger.warning("⚠️ Only OpenAI GPT is supported right now. Defaulting to OpenAI GPT.")
        SystemSettings.model_type = "openai"
        get_api_key()  # ✅ Ensure API key is set for OpenAI even if defaulted

def get_api_key():
    """Prompt the user to enter their OpenAI API Key and store it securely for the session."""
    if SystemSettings.api_key:  # ✅ If already set, don't ask again
        return

    while True:
        key = input("🔑 Enter your OpenAI API Key: ").strip()
        if key:
            SystemSettings.set_api_key(key)  # ✅ Store in `SystemSettings`
            break
        else:
            logger.error("❌ API Key cannot be empty. Please enter a valid key.")

def get_model_name():
    """Ask the user to select a model from available OpenAI models."""
    
    if SystemSettings.model_type != "openai":
        logger.warning("⚠️ No other LLMs are available yet. Defaulting to 'gpt-3.5-turbo'.")
        SystemSettings.model_name = "gpt-3.5-turbo"
        return

    available_models = fetch_openai_models()

    if not available_models:
        logger.warning("⚠️ No models retrieved. Defaulting to 'gpt-3.5-turbo'.")
        SystemSettings.model_name = "gpt-3.5-turbo"
        return

    print("\n🧠 Available OpenAI Models:")
    for idx, model in enumerate(available_models, start=1):
        print(f"{idx} - {model}")

    while True:
        choice = input(f"\nSelect a model (1-{len(available_models)}) or press Enter for default (gpt-3.5-turbo): ").strip()

        if not choice:  # Default model
            SystemSettings.model_name = "gpt-3.5-turbo"
            break

        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(available_models):
                SystemSettings.model_name = available_models[choice - 1]
                logger.info(f"✅ Model set to {SystemSettings.model_name}")
                break
            else:
                print("❌ Invalid selection. Please enter a valid number.")
        else:
            print("❌ Invalid input. Please enter a number.")

def select_csv_file():
    """Allow the user to select a CSV file from `data/`."""
    csv_files = list_files(DATA_DIR, ".csv")
    if not csv_files:
        logger.error("❌ No CSV files found in `data/`. Cannot proceed.")
        exit(1)

    print("\n📂 Available CSV Files:")
    for idx, file in enumerate(csv_files, start=1):
        print(f"{idx} - {file}")

    while True:
        choice = input("\nSelect a CSV file (Enter number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(csv_files):
            selected_csv = os.path.join(DATA_DIR, csv_files[int(choice) - 1])
            logger.info(f"✅ Selected CSV file: {selected_csv}")
            return selected_csv  # ✅ Now returns the correct file path
        else:
            print("❌ Invalid choice. Please enter a valid number.")

def select_csv_column(csv_file):
    """Allow the user to select a column from the chosen CSV file."""
    df = load_csv(csv_file)  # ✅ Now using file_handler
    if df is None or df.empty:  # ✅ Now checks if it's empty
        logger.error("❌ CSV file is empty or failed to load.")
        exit(1)

    print("\n📊 Available Columns in CSV:")
    for idx, column in enumerate(df.columns, start=1):
        print(f"{idx} - {column}")

    while True:
        choice = input("\nEnter column number to use for prediction: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(df.columns):
            selected_column = df.columns[int(choice) - 1]
            logger.info(f"✅ Selected column: {selected_column}")
            return selected_column
        else:
            print("❌ Invalid choice. Please enter a valid number.")