from collections import defaultdict

def validate_dataset_format(dataset: list) -> dict:
    """
    Validate the format of the dataset.
    
    Checks include:
      - Each entry must be a dict.
      - Each entry must have a 'messages' list.
      - Each message must have the keys 'role' and 'content'.
      - Messages should not include unexpected keys (only allow 'role', 'content', 'name', 'function_call', and 'weight').
      - The 'role' field must be one of "system", "user", "assistant", or "function".
      - The 'content' should be a string (unless a function call is present).
      - Each conversation should have at least one message from the assistant.
    
    Args:
        dataset (list): List of dataset examples.
        
    Returns:
        dict: A dictionary mapping error types to their counts.
    """
    format_errors = defaultdict(int)

    for ex in dataset:
        if not isinstance(ex, dict):
            format_errors["data_type"] += 1
            continue

        messages = ex.get("messages", None)
        if not messages:
            format_errors["missing_messages_list"] += 1
            continue

        for message in messages:
            if "role" not in message or "content" not in message:
                format_errors["message_missing_key"] += 1

            if any(k not in ("role", "content", "name", "function_call", "weight") for k in message):
                format_errors["message_unrecognized_key"] += 1

            if message.get("role", None) not in ("system", "user", "assistant", "function"):
                format_errors["unrecognized_role"] += 1

            content = message.get("content", None)
            function_call = message.get("function_call", None)
            if (not content and not function_call) or not isinstance(content, str):
                format_errors["missing_content"] += 1

        if not any(message.get("role", None) == "assistant" for message in messages):
            format_errors["example_missing_assistant_message"] += 1

    return format_errors

def print_format_errors(format_errors: dict):
    """
    Print the format errors found in the dataset.
    
    Args:
        format_errors (dict): Dictionary of error counts.
    """
    if format_errors:
        print("Found errors:")
        for k, v in format_errors.items():
            print(f"{k}: {v}")
    else:
        print("No errors found")
