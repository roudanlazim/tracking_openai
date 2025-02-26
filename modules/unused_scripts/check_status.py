import openai
import time
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def check_fine_tune_status(fine_tune_id):
    while True:
        response = openai.FineTune.retrieve(fine_tune_id)
        status = response["status"]
        print(f"Fine-tune status: {status}")

        if status in ["succeeded", "failed"]:
            break
        time.sleep(30)

    if status == "succeeded":
        fine_tuned_model = response["fine_tuned_model"]
        print(f"✅ Fine-tuning complete! Model ID: {fine_tuned_model}")
        return fine_tuned_model
    else:
        print("❌ Fine-tuning failed.")
        return None

if __name__ == "__main__":
    fine_tune_id = input("Enter your Fine-tune ID: ")
    check_fine_tune_status(fine_tune_id)
