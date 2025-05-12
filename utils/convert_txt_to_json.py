import os
import json

def convert_txt_to_json(input_txt_path):
    """
    Given a path to a .txt file, read all lines and produce
    a JSON file with the same name (but .json extension) in the same directory.
    """
    # 1. Read the text lines
    with open(input_txt_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    # 2. Build the JSON data
    data = {
        "content": lines
    }

    # 3. Construct output path (replace .txt with .json)
    base, ext = os.path.splitext(input_txt_path)
    output_json_path = base + ".json"

    # 4. Write data to JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Converted '{input_txt_path}' -> '{output_json_path}'")

if __name__ == "__main__":
    # Example usage with your given paths:
    input_file = r"C:\Users\Shaalan\tracking_openai\data\prompts\pvr_matcher_prompt\scan_group_prompt.txt"
    convert_txt_to_json(input_file)
