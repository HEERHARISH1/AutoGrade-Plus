"""Quick test of JSON extraction"""
import sys
sys.path.insert(0, 'c:/Users/heerh/OneDrive/Desktop/FAST/7th_Semester/GenAI/Project_i222371')

from src.utils.grading_validator import extract_json_from_text

# Test with markdown
test1 = """```json
{"score": 8, "max_score": 10}
```"""

result1 = extract_json_from_text(test1)
print("Test 1 (markdown):", "PASS" if result1 else "FAIL")
if result1:
    print("  Extracted:", result1[:50])

# Test with extra text
test2 = """Here is the result:
{"score": 7, "max_score": 10}
Done!"""

result2 = extract_json_from_text(test2)
print("Test 2 (extra text):", "PASS" if result2 else "FAIL")
if result2:
    print("  Extracted:", result2[:50])

# Test plain JSON
test3 = '{"score": 10, "max_score": 10}'
result3 = extract_json_from_text(test3)
print("Test 3 (plain):", "PASS" if result3 else "FAIL")

print("\nAll tests completed!")
