import tiktoken

def count_tokens(text, model="gpt-4-turbo"):
    """Counts tokens in a given text using OpenAI tokenizer."""
    tokenizer = tiktoken.encoding_for_model(model)
    return len(tokenizer.encode(text))

if __name__ == "__main__":
    test_text = "This is a test sentence to check token counting accuracy."
    print(f"Token Count: {count_tokens(test_text)}")
