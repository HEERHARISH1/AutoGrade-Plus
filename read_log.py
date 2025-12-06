import sys
try:
    with open('debug_log.txt', 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        print("--- START OF LOG ---")
        print(content)
        print("--- END OF LOG ---")
except Exception as e:
    print(f"Error reading log: {e}")
