import json

def load_dataset(data_path: str):
    """
    Load a JSONL dataset from the given file path.
    
    Args:
        data_path (str): Path to the JSONL file.
        
    Returns:
        list: List of dataset examples (each example is a dict).
    """
    with open(data_path, 'r', encoding='utf-8') as f:
        dataset = [json.loads(line) for line in f]
    return dataset

def print_initial_stats(dataset: list):
    """
    Print initial statistics of the dataset.
    
    Args:
        dataset (list): List of dataset examples.
    """
    print("Num examples:", len(dataset))
    if dataset:
        print("First example:")
        for message in dataset[0].get("messages", []):
            print(message)
