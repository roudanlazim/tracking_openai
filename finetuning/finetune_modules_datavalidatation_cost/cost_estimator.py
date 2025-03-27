def estimate_costs(convo_lens: list,
                   n_train_examples: int,
                   target_epochs: int = 3,
                   min_target_examples: int = 100,
                   max_target_examples: int = 25000,
                   min_default_epochs: int = 1,
                   max_default_epochs: int = 25,
                   max_tokens_per_example: int = 16385) -> dict:
    """
    Estimate fine-tuning cost and appropriate number of epochs.
    
    This function uses the total token count per conversation and the number of training examples
    to approximate how many tokens will be charged for during fine-tuning and adjusts the number of epochs.
    
    Args:
        convo_lens (list): List of token counts for each conversation.
        n_train_examples (int): Number of training examples.
        target_epochs (int): Target epochs for training.
        min_target_examples (int): Minimum total examples desired.
        max_target_examples (int): Maximum total examples allowed.
        min_default_epochs (int): Minimum default epochs.
        max_default_epochs (int): Maximum default epochs.
        max_tokens_per_example (int): Maximum tokens per example (to cap token count).
        
    Returns:
        dict: A dictionary containing:
            - n_epochs: Number of epochs to train.
            - billing_tokens: Total tokens in the dataset (capped per example).
            - total_tokens_charged: Total tokens charged (n_epochs * billing_tokens).
    """
    n_epochs = target_epochs
    if n_train_examples * target_epochs < min_target_examples:
        n_epochs = min(max_default_epochs, min_target_examples // n_train_examples)
    elif n_train_examples * target_epochs > max_target_examples:
        n_epochs = max(min_default_epochs, max_target_examples // n_train_examples)

    n_billing_tokens_in_dataset = sum(min(max_tokens_per_example, length) for length in convo_lens)
    
    return {
        "n_epochs": n_epochs,
        "billing_tokens": n_billing_tokens_in_dataset,
        "total_tokens_charged": n_epochs * n_billing_tokens_in_dataset
    }
