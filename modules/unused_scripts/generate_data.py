import pandas as pd
import os
import logging
import shutil
from sklearn.model_selection import train_test_split
from datetime import datetime

# Create logs directory if not exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Generate log filename with timestamp
log_filename = os.path.join(LOG_DIR, f"generate_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Configure logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def backup_old_data(train_csv, test_csv):
    """Backup previous train and test datasets if they exist."""
    if os.path.exists(train_csv):
        shutil.move(train_csv, train_csv.replace(".csv", "_backup.csv"))
        logging.info(f"🔄 Previous training data backed up: {train_csv}_backup.csv")

    if os.path.exists(test_csv):
        shutil.move(test_csv, test_csv.replace(".csv", "_backup.csv"))
        logging.info(f"🔄 Previous test data backed up: {test_csv}_backup.csv")

def generate_training_data(input_csv, train_csv, test_csv, test_size=0.2):
    """Generate training and test datasets from the input file."""
    try:
        logging.info(f"📥 Loading dataset: {input_csv}")
        
        df = pd.read_csv(input_csv)
        
        # Validate if dataset is not empty
        if df.empty:
            logging.error("❌ Error: The input CSV file is empty.")
            print("❌ Error: The input CSV file is empty.")
            return
        
        # Backup previous datasets before generating new ones
        backup_old_data(train_csv, test_csv)

        # Splitting the dataset
        train, test = train_test_split(df, test_size=test_size, random_state=42)
        
        # Saving new datasets
        train.to_csv(train_csv, index=False)
        test.to_csv(test_csv, index=False)

        logging.info(f"✅ New training data saved to: {train_csv} ({len(train)} records)")
        logging.info(f"✅ New test data saved to: {test_csv} ({len(test)} records)")

        print(f"✅ Training data saved to {train_csv} ({len(train)} records)")
        print(f"✅ Test data saved to {test_csv} ({len(test)} records)")

    except FileNotFoundError as e:
        logging.error(f"❌ Error: File not found - {e}")
        print(f"❌ Error: File not found - {e}")

    except pd.errors.ParserError as e:
        logging.error(f"❌ Error: Parsing CSV failed - {e}")
        print(f"❌ Error: Parsing CSV failed - {e}")

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    input_csv = "data/training_dataset_status_elements.csv"
    train_csv = "data/train.csv"
    test_csv = "data/test.csv"

    logging.info("🚀 Starting Training Data Generation...")
    generate_training_data(input_csv, train_csv, test_csv)
    logging.info("🎯 Training Data Generation Completed!")
