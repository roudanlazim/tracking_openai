# AI Shipment Tracking Pipeline

## Overview
This project provides an AI-driven shipment tracking pipeline that processes shipment scan histories, applies structured decision trees, and predicts shipment statuses using OpenAI's GPT models.
It supports CSV-based batch processing, outputs results in both CSV and JSON, and logs all key events for debugging and tracking.

It's is really for testing lots of predictions using different models etc. 

---

## Core Features

### User Input & Configuration
- Select an AI model (OpenAI GPT or future models).
- Choose a specific model (e.g., `gpt-3.5-turbo` or `gpt-4`).
- Enter an API key for authentication.
- Pick an input CSV file for processing.
- Choose the column containing shipment scan histories.
- Select a JSON-based decision tree prompt to structure AI responses.

### Processing & AI Prediction
- Reads the selected CSV file.
- Formats shipment history into a structured AI prompt using a decision tree.
- Queries OpenAI's API with binary-mapped Yes/No questions for efficiency.
- Retrieves the most probable shipment status (e.g., "Delivered", "In Transit", "Exception").

### Output Generation
- Saves results in both CSV and JSON formats:
  - CSV includes token usage and cost estimations.
  - JSON includes full structured logs for database storage.
- The output file is automatically opened after processing.

---

## Key Modules & Responsibilities

| Module                 | Description                                         |
|------------------------|-----------------------------------------------------|
| `run_predicting.py`    | Main script orchestrating the pipeline.            |
| `user_input.py`        | Handles user selections (CSV, model, column, prompt). |
| `ai_model.py`         | Calls OpenAI's API and retrieves AI predictions.    |
| `prediction_processor.py` | Processes CSV rows and applies AI predictions.    |
| `file_handler.py`      | Loads/saves JSON, CSV, and manages file operations. |
| `settings.json`        | Stores default settings like model type & file paths. |
| `settings_loader.py`   | Loads and manages settings dynamically.            |
| `prompt_generator.py`  | Generates structured AI prompts from JSON templates. |
| `model_handler.py`     | Fetches available AI models via API.               |
| `logging_utils.py`     | Handles logging for debugging and tracking.        |

---

## How It Works (Step-by-Step)

1. Run `run_predicting.py`.  
2. Select required options:
   - AI model type (default: OpenAI GPT).
   - Model name (e.g., `gpt-3.5-turbo`).
   - CSV file and column for shipment tracking data.
   - Predefined AI prompt (stored as JSON).  
3. The system loads `settings.json` and decision tree prompts.  
4. Processes each row in the CSV file:
   - Formats shipment history into a structured decision-based prompt.
   - AI model predicts the correct status.
   - Logs the prediction (JSON + CSV output).  
5. Saves the results:
   - CSV: For easy business review.
   - JSON: For database storage.
6. Opens the results file for review.

---

## AI Prompting System

- Uses a JSON-based prompt template (`system_prompt.json`).
- Implements a structured Yes/No decision tree.
- Ensures consistent AI responses with clear logic.

### Example Statuses
- **In Transit** – Moving between facilities.
- **Out for Delivery** – With the local courier.
- **Delivered** – Successfully received.
- **Exception** – Delivery failed or delayed.
- **Return to Sender** – Sent back due to an issue.

---

## Error Handling & Logging

- Logs all operations to `logs/app.log` for debugging.
- Handles missing files & settings gracefully.
- Retries AI requests on failure (with exponential backoff).
- Warns users before incurring API costs.

---

## Planned Future Enhancements

### Batch Processing Optimization
- Current Issue: Processing happens row-by-row.
- Improvement: Implement batch processing (e.g., process 10-50 rows at a time).
- Benefit: Significantly improves performance.

### Web Interface for User Selections
- Current Issue: CLI-based interactions.
- Improvement: Create a Flask/FastAPI-based UI for selecting models, files, and prompts.
- Benefit: Improves usability.

### Secure API Key Handling
- Current Issue: API keys are stored in memory (`SystemSettings`).
- Improvement: Use `.env` files or secure vaults for API key storage.
- Benefit: Improves security.

### Real-time Dashboard & Visualization
- Current Issue: Only logs are available, no live tracking.
- Improvement: Graphically display predictions using Plotly/Streamlit.
- Benefit: Enables real-time tracking.

### Live Data Processing
- Current Issue: Only works with static CSVs.
- Improvement: Support real-time shipment updates via Kafka/RabbitMQ.
- Benefit: Enables live tracking.

### Better Token Cost Estimation
- Current Issue: Uses a static token pricing model.
- Improvement: Fetch dynamic OpenAI pricing via API.
- Benefit: More accurate cost calculations.

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- An OpenAI API Key
- Install dependencies:

```bash
pip install -r requirements.txt