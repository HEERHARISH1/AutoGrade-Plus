"""
Test script to verify JSON parsing improvements in grading_validator.py
"""

import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, 'c:/Users/heerh/OneDrive/Desktop/FAST/7th_Semester/GenAI/Project_i222371')

from src.utils.grading_validator import validate_and_fix_grading, extract_json_from_text

# Test cases with various malformed outputs
test_cases = [
    {
        "name": "Valid JSON with markdown code blocks",
        "input": """```json
{
  "score": 8,
  "max_score": 10,
  "feedback": "Good work!",
  "breakdown": {
    "Correctness": {"points": 5, "max": 5, "comment": "Perfect"},
    "Style": {"points": 3, "max": 5, "comment": "Needs improvement"}
  }
}
```"""
    },
    {
        "name": "Valid JSON with text before and after",
        "input": """Here is the grading result:
{
  "score": 7,
  "max_score": 10,
  "feedback": "Decent attempt",
  "breakdown": {
    "Logic": {"points": 4, "max": 5, "comment": "Minor error"},
    "Documentation": {"points": 3, "max": 5, "comment": "Incomplete"}
  }
}
Hope this helps!"""
    },
    {
        "name": "Valid JSON only",
        "input": """{
  "score": 10,
  "max_score": 10,
  "feedback": "Excellent!",
  "breakdown": {
    "All Criteria": {"points": 10, "max": 10, "comment": "Perfect score"}
  }
}"""
    },
    {
        "name": "JSON with math errors (score mismatch)",
        "input": """{
  "score": 10,
  "max_score": 10,
  "feedback": "Good",
  "breakdown": {
    "Criterion1": {"points": 3, "max": 5, "comment": "OK"},
    "Criterion2": {"points": 4, "max": 5, "comment": "Good"}
  }
}"""
    },
    {
        "name": "JSON with points exceeding max",
        "input": """{
  "score": 12,
  "max_score": 10,
  "feedback": "Over-scored",
  "breakdown": {
    "Criterion1": {"points": 7, "max": 5, "comment": "Too high"},
    "Criterion2": {"points": 5, "max": 5, "comment": "OK"}
  }
}"""
    }
]

print("=" * 80)
print("TESTING JSON PARSING AND VALIDATION")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"Test {i}: {test['name']}")
    print(f"{'='*80}")
    print(f"\n📥 INPUT (first 200 chars):")
    print(test['input'][:200])
    print("...")
    
    try:
        # Test extraction
        extracted = extract_json_from_text(test['input'])
        if extracted:
            print(f"\n✅ JSON EXTRACTED SUCCESSFULLY")
            print(f"Length: {len(extracted)} characters")
        else:
            print(f"\n❌ FAILED TO EXTRACT JSON")
            continue
        
        # Test validation
        result = validate_and_fix_grading(test['input'])
        
        print(f"\n📊 VALIDATION RESULT:")
        print(f"  Score: {result['score']} / {result['max_score']}")
        print(f"  Feedback: {result['feedback'][:100]}...")
        print(f"  Breakdown items: {len(result.get('breakdown', {}))}")
        
        if 'validation_notes' in result:
            print(f"\n⚠️ VALIDATION CORRECTIONS:")
            for note in result['validation_notes']:
                print(f"    - {note}")
        else:
            print(f"\n✅ No validation corrections needed")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*80}")
print("TESTING COMPLETE")
print(f"{'='*80}")
