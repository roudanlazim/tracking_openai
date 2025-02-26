import openai
import os
import logging
from dotenv import load_dotenv
from utils import load_json

# API Key securely from config.. 
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("ERROR: OPENAI_API_KEY not found in environment variables.")

openai.api_key = api_key  # Ensure API key is in correct project

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def predict_status(ai_story, fine_tuned_model, valid_statuses_file, results_log="predictions_log.csv"):
    """Predict the final status using the fine-tuned model."""
    try:
        # Load valid statuses
        if not os.path.exists(valid_statuses_file):
            raise FileNotFoundError(f"ERROR: Valid statuses file not found at {valid_statuses_file}")

        valid_statuses = load_json(valid_statuses_file)

        logging.info(f"📤 Sending request to model {fine_tuned_model}...")

        # ✅ Correct OpenAI API call (without organization & project)
        response = openai.chat.completions.create(
            model=fine_tuned_model,
            messages=[
                {"role": "system", "content": "You are a logistics assistant. Provide the most accurate shipment status."},
                {"role": "user", "content": ai_story}
            ],
            temperature=0  # ✅ Ensures consistency
        )

        # ✅ Extract the response
        predicted_status = response.choices[0].message.content.strip()
        logging.info(f"✅ Model Response: {predicted_status}")

        # ✅ Validate the predicted status
        if predicted_status not in valid_statuses:
            final_status = "FLAGGED: Invalid prediction"
            logging.warning(f"⚠️ Prediction flagged as invalid: {predicted_status}")
        else:
            final_status = predicted_status

        # ✅ Log the result
        with open(results_log, "a") as log:
            log.write(f"{ai_story},{final_status}\n")

        logging.info(f"📦 Predicted Status: {final_status}")
        return final_status

    except openai.OpenAIError as e:
        logging.error(f"❌ API Error: {str(e)}")
        return "ERROR: API Call Failed"
    except Exception as e:
        logging.error(f"❌ Unexpected Error: {str(e)}")
        return "ERROR: Prediction Failed"

if __name__ == "__main__":
    # ✅ Prompt for model ID
    fine_tuned_model = input("Enter your Fine-tuned Model ID: ").strip()

    # ✅ Test Prediction
    test_story = "At first, it was Shipment collected, then it was Out for delivery, then it was Delivered to postbox."
    status_elements_file = "data/status_elements.json"

    print("\n🔍 Running Prediction...\n")
    predicted_status = predict_status(test_story, fine_tuned_model, status_elements_file)
    print(f"\n🎯 Final Prediction: {predicted_status}\n")
