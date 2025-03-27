import tiktoken
import numpy as np

# Use the encoding for gpt-3.5-turbo (cl100k_base)
encoding = tiktoken.get_encoding("cl100k_base")

def num_tokens_from_messages(messages: list, tokens_per_message: int = 3, tokens_per_name: int = 1) -> int:
    """
    Calculate the number of tokens used by a list of messages.
    
    Simplified version inspired by:
    https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    
    Args:
        messages (list): List of message dictionaries.
        tokens_per_message (int): Additional tokens per message.
        tokens_per_name (int): Additional tokens per name field.
    
    Returns:
        int: Total number of tokens.
    """
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with additional tokens
    return num_tokens

def num_assistant_tokens_from_messages(messages: list) -> int:
    """
    Calculate the number of tokens in the assistant's messages.
    
    Args:
        messages (list): List of message dictionaries.
    
    Returns:
        int: Total number of tokens in assistant messages.
    """
    num_tokens = 0
    for message in messages:
        if message.get("role") == "assistant":
            num_tokens += len(encoding.encode(message.get("content", "")))
    return num_tokens

def print_distribution(values: list, name: str):
    """
    Print distribution statistics for a list of numerical values.
    
    Args:
        values (list): List of numerical values.
        name (str): Name for the distribution being printed.
    """
    print(f"\n#### Distribution of {name}:")
    print(f"min / max: {min(values)}, {max(values)}")
    print(f"mean / median: {np.mean(values)}, {np.median(values)}")
    print(f"p5 / p95: {np.quantile(values, 0.1)}, {np.quantile(values, 0.9)}")
