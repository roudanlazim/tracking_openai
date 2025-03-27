# run_analysis_dataprep.py

from data_loader import load_dataset, print_initial_stats
from data_validator import validate_dataset_format, print_format_errors
from token_utils import num_tokens_from_messages, num_assistant_tokens_from_messages, print_distribution
from cost_estimator import estimate_costs

def analyze_dataset(dataset, max_tokens_per_example=16385):
    """
    Analyzes the dataset for missing messages, token counts, and other metrics.
    Prints out distributions and warnings if token limits are exceeded.
    Returns a dictionary with analysis results.
    """
    n_missing_system = 0
    n_missing_user = 0
    n_messages = []
    convo_lens = []
    assistant_message_lens = []

    for ex in dataset:
        messages = ex.get("messages", [])
        if not any(message.get("role") == "system" for message in messages):
            n_missing_system += 1
        if not any(message.get("role") == "user" for message in messages):
            n_missing_user += 1
        n_messages.append(len(messages))
        convo_lens.append(num_tokens_from_messages(messages))
        assistant_message_lens.append(num_assistant_tokens_from_messages(messages))
    
    print("Num examples missing system message:", n_missing_system)
    print("Num examples missing user message:", n_missing_user)
    print_distribution(n_messages, "num_messages_per_example")
    print_distribution(convo_lens, "num_total_tokens_per_example")
    print_distribution(assistant_message_lens, "num_assistant_tokens_per_example")
    
    n_too_long = sum(l > max_tokens_per_example for l in convo_lens)
    print(f"\n{n_too_long} examples may be over the {max_tokens_per_example} token limit, they will be truncated during fine-tuning")
    
    return {
        "n_missing_system": n_missing_system,
        "n_missing_user": n_missing_user,
        "n_messages": n_messages,
        "convo_lens": convo_lens,
        "assistant_message_lens": assistant_message_lens,
        "n_too_long": n_too_long
    }

def main():
    DATA_PATH = "data/toy_chat_fine_tuning.jsonl"
    dataset = load_dataset(DATA_PATH)
    
    # Print initial stats from the loader
    print_initial_stats(dataset)
    
    # Validate dataset format
    format_errors = validate_dataset_format(dataset)
    print_format_errors(format_errors)
    
    # Analyze dataset for token usage and message distribution
    analysis_results = analyze_dataset(dataset)
    
    # Estimate fine-tuning cost
    n_train_examples = len(dataset)
    cost_info = estimate_costs(analysis_results["convo_lens"], n_train_examples)
    
    print(f"\nDataset has ~{cost_info['billing_tokens']} tokens that will be charged for during training")
    print(f"By default, you'll train for {cost_info['n_epochs']} epochs on this dataset")
    print(f"By default, you'll be charged for ~{cost_info['total_tokens_charged']} tokens")

if __name__ == "__main__":
    main()
