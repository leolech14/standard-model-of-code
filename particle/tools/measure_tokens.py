import json
import sys
import tiktoken

def count_tokens(file_path):
    try:
        with open(file_path, "r") as f:
            content = f.read()
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(content))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return -1

if len(sys.argv) < 2:
    print("Usage: python measure_tokens.py <file1.json> [file2.json...]")
    sys.exit(1)

for arg in sys.argv[1:]:
    tokens = count_tokens(arg)
    print(f"{arg}: {tokens:,} tokens")
