import os
import getpass
from modules.logging_utils import logger
from modules.system_settings import SystemSettings
from modules.file_handler import load_csv, list_files
from modules.ai_model import fetch_openai_models
from modules.json_handler import list_json_files  

DATA_DIR = "data/"

### ✅ MODEL SELECTION FUNCTIONS
def get_model_type():
    """Ask the user to select the AI model type (e.g., OpenAI)."""
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
    if SystemSettings.api_key:
        return  # ✅ If already set, don’t ask again

    while True:
        key = getpass.getpass("🔑 Enter your OpenAI API Key (hidden): ").strip()  # ✅ Now hidden input
        if key:
            SystemSettings.api_key = key  # ✅ Store the API key securely
            break
        else:
            logger.error("❌ API Key cannot be empty. Please enter a valid key.")

def get_model_name():
    """Ask the user to select a model from available OpenAI models."""
    
    if SystemSettings.model_type != "openai":
        logger.warning("⚠️ No other LLMs are available yet. Defaulting to 'gpt-4o-mini'.")
        SystemSettings.model_name = "gpt-4o-mini"
        return

    available_models = fetch_openai_models()

    if not available_models:
        logger.warning("⚠️ No models retrieved. Defaulting to 'gpt-4o-mini'.")
        SystemSettings.model_name = "gpt-4o-mini"
        return

    print("\n🧠 Available OpenAI Models:")
    for idx, model in enumerate(available_models, start=1):
        print(f"{idx} - {model}")

    while True:
        choice = input(f"\nSelect a model (1-{len(available_models)}) or press Enter for default (gpt-4o-mini): ").strip()

        if not choice:  # Default model
            SystemSettings.model_name = "gpt-4o-mini"
            logger.info(f"✅ Defaulting to model: {SystemSettings.model_name}")  # ✅ Log default selection
            return  # ✅ Ensure function exits properly

        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(available_models):
                SystemSettings.model_name = available_models[choice - 1]
                logger.info(f"✅ Model set to {SystemSettings.model_name}")
                return  # ✅ Ensure function exits properly
            else:
                print("❌ Invalid selection. Please enter a valid number.")
        else:
            print("❌ Invalid input. Please enter a number.")

### ✅ CSV & COLUMN SELECTION FUNCTIONS
def select_csv_file():
    """Allow user to select a CSV file from `data/` and cache the selection."""
    print(f"\n🟢 DEBUG: Checking for CSV files in '{os.path.abspath(DATA_DIR)}'...")  # ✅ Debug print

    csv_files = list_files("", ".csv")  # ✅ Uses `DATA_DIR` from `file_handler.py`

    if not csv_files:
        logger.error("❌ No CSV files found in `data/`. Exiting.")
        print(f"\n❌ DEBUG: No CSV files found in '{os.path.abspath(DATA_DIR)}'. Exiting...")
        exit(1)

    print("\n📂 Available CSV Files:")
    for idx, file in enumerate(csv_files, start=1):
        print(f"{idx} - {file}")

    while True:
        choice = input("\nSelect a CSV file (Enter number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(csv_files):
            selected_csv = os.path.join(DATA_DIR, csv_files[int(choice) - 1])  # ✅ Correct path usage
            logger.info(f"✅ Selected CSV file: {selected_csv}")
            print(f"\n🟢 DEBUG: Selected CSV file: {selected_csv}")  # ✅ Debug print
            SystemSettings.input_file = selected_csv
            print(f"\n🟢 DEBUG: CSV file set in `SystemSettings.input_file`: {SystemSettings.input_file}")  # ✅ Debug print
            return selected_csv

        else:
            print("❌ Invalid choice. Please enter a valid number.")

def select_csv_column():
    """Allow user to select a column from the chosen CSV file and cache the selection."""
    csv_file = SystemSettings.input_file
    print(f"\n🟢 DEBUG: Loading selected CSV file: `{csv_file}`...")  # ✅ Debug print
    df = load_csv(csv_file)  # ✅ Ensure file is actually being loaded

    
    if df is None or df.empty:
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
            SystemSettings.selected_column = selected_column
            return selected_column
        else:
            print("❌ Invalid choice. Please enter a valid number.")

### ✅ PROMPT SELECTION (Now Calls `prompt_generator.py`)
def select_prompt():
    """Allow user to select an existing JSON prompt from `data/prompts/`."""
    prompt_files = list_json_files("data/prompts/")  # ✅ Uses json_handler.py

    if not prompt_files:
        logger.error("❌ No available prompt files found in `data/prompts/`. Exiting.")
        exit(1)

    # ✅ Remove duplicate printing here (list_json_files() already prints available JSON files)

    while True:
        choice = input("\nSelect a system prompt (Enter number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(prompt_files):
            selected_prompt = os.path.join("data/prompts/", prompt_files[int(choice) - 1])
            logger.info(f"✅ Selected system prompt: {selected_prompt}")
            SystemSettings.prompt_file = selected_prompt
            return selected_prompt
        else:
            print("❌ Invalid choice. Please enter a valid number.")

### ✅ FINAL CONFIRMATION
def confirm_selection():
    """Ask the user to confirm selections before proceeding."""
    print("\n✅ Review Your Selections:")
    print(f"🔹 Model Type: {SystemSettings.model_type}")
    print(f"🔹 Model Name: {SystemSettings.model_name}")
    print(f"🔹 Input CSV File: {SystemSettings.input_file}")
    print(f"🔹 Selected Column: {SystemSettings.selected_column}")
    print(f"🔹 JSON Prompt File: {SystemSettings.prompt_file}")
    print("\n⚠️ Do you want to proceed? Running this will incur API costs.")

    return input("\nType 'yes' to proceed or 'no' to cancel: ").strip().lower() == "yes"