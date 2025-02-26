import csv
import logging
import os
from dotenv import load_dotenv
from predict import predict_status  # ✅ Importing prediction function

# ✅ Load API Key securely
load_dotenv()

# ✅ Paths to dataset files
test_data_file = "data/test.csv"
status_elements_file = "data/status_elements.json"
results_log = "data/evaluation_results.csv"

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def evaluate_model(fine_tuned_model):
    """Runs predictions on a test dataset and calculates accuracy."""
    correct = 0
    total = 0
    mismatches = []

    # ✅ Check if test dataset exists
    if not os.path.exists(test_data_file):
        logging.error(f"❌ ERROR: Test dataset file not found at {test_data_file}")
        return

    logging.info(f"📥 Loading test dataset: {test_data_file}")

    # ✅ Load test dataset
    with open(test_data_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        test_cases = list(reader)

    if not test_cases:
        logging.error("❌ ERROR: No test cases found in the dataset.")
        return

    logging.info(f"🔍 Running {len(test_cases)} test predictions...")

    # ✅ Run predictions & compare results
    with open(results_log, "w", encoding="utf-8", newline="") as log_file:
        writer = csv.writer(log_file)
        writer.writerow(["AI Story", "Expected Status", "Predicted Status", "Match?"])

        for case in test_cases:
            ai_story = case["AiStory"]
            expected_status = case["ExpectedStatus"].strip()

            # ✅ Calls predict.py function
            predicted_status = predict_status(ai_story, fine_tuned_model, status_elements_file)

            match = "1" if predicted_status == expected_status else "0"
            if match == "0":
                mismatches.append((ai_story, expected_status, predicted_status))

            writer.writerow([ai_story, expected_status, predicted_status, match])
            total += 1
            correct += 1 if match == "1" else 0

    # ✅ Calculate Accuracy
    accuracy = (correct / total) * 100 if total > 0 else 0
    logging.info(f"\n🎯 Model Accuracy: {accuracy:.2f}% ({correct}/{total} correct)")

    # ✅ Show mismatched predictions
    if mismatches:
        logging.warning("\n⚠️ Mismatched Predictions:")
        for story, expected, predicted in mismatches[:5]:  # Show only first 5 mismatches
            logging.warning(f"❌ AI Story: {story}\n   Expected: {expected} | Predicted: {predicted}\n")

    return accuracy

if __name__ == "__main__":
    fine_tuned_model = input("Enter your Fine-tuned Model ID: ").strip()
    evaluate_model(fine_tuned_model)
