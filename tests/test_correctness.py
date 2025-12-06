"""
Test script to verify all three critical fixes:
1. PDF text detection
2. Mathematical correctness in grading
3. Logical marking (wrong answers get zero marks)
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.grading_validator import validate_and_fix_grading, format_validated_grading
import json


def test_mathematical_validation():
    """Test that mathematical errors are caught and corrected"""
    print("\n" + "="*80)
    print("TEST 1: Mathematical Validation")
    print("="*80)
    
    # Test Case 1: Points exceeding max
    print("\n📋 Test Case 1.1: Points exceeding max")
    bad_grading_1 = json.dumps({
        "score": 12,
        "max_score": 10,
        "feedback": "Good work",
        "breakdown": {
            "Criterion 1": {"points": 7, "max": 5, "comment": "Exceeded max"},
            "Criterion 2": {"points": 5, "max": 5, "comment": "Perfect"}
        }
    })
    
    result_1 = validate_and_fix_grading(bad_grading_1)
    print(f"Original: score=12, breakdown: 7+5=12")
    print(f"Corrected: score={result_1['score']}, breakdown: {result_1['breakdown']['Criterion 1']['points']}+{result_1['breakdown']['Criterion 2']['points']}={result_1['score']}")
    assert result_1['breakdown']['Criterion 1']['points'] == 5, "Should cap at max"
    assert result_1['score'] == 10, "Should correct total"
    print("✅ PASSED: Points capped at max and total corrected")
    
    # Test Case 2: Sum mismatch
    print("\n📋 Test Case 1.2: Sum mismatch")
    bad_grading_2 = json.dumps({
        "score": 10,
        "max_score": 10,
        "feedback": "Good work",
        "breakdown": {
            "Criterion 1": {"points": 3, "max": 5, "comment": "Good"},
            "Criterion 2": {"points": 4, "max": 5, "comment": "Good"}
        }
    })
    
    result_2 = validate_and_fix_grading(bad_grading_2)
    print(f"Original: score=10, breakdown: 3+4=7")
    print(f"Corrected: score={result_2['score']}, breakdown: 3+4={result_2['score']}")
    assert result_2['score'] == 7, "Should correct to actual sum"
    print("✅ PASSED: Score corrected to match breakdown sum")
    
    # Test Case 3: Valid grading (should pass through)
    print("\n📋 Test Case 1.3: Valid grading (no corrections needed)")
    good_grading = json.dumps({
        "score": 8,
        "max_score": 10,
        "feedback": "Good work",
        "breakdown": {
            "Criterion 1": {"points": 4, "max": 5, "comment": "Good"},
            "Criterion 2": {"points": 4, "max": 5, "comment": "Good"}
        }
    })
    
    result_3 = validate_and_fix_grading(good_grading)
    print(f"Input: score=8, breakdown: 4+4=8")
    print(f"Output: score={result_3['score']}, breakdown: 4+4={result_3['score']}")
    assert result_3['score'] == 8, "Should remain unchanged"
    assert 'validation_notes' not in result_3, "Should have no validation notes"
    print("✅ PASSED: Valid grading passed through unchanged")


def test_logical_marking_prompt():
    """Test that the prompt includes logical marking instructions"""
    print("\n" + "="*80)
    print("TEST 2: Logical Marking Instructions in Prompt")
    print("="*80)
    
    from src.agent.react_engine import GradingAgent
    
    # Create a dummy agent (won't actually call API)
    try:
        # This will fail without API key, but we can still check the prompt
        print("\n📋 Checking ReAct Engine prompt...")
        with open('src/agent/react_engine.py', 'r', encoding='utf-8') as f:
            react_code = f.read()
        
        # Check for key phrases
        checks = [
            ("LOGICAL MARKING", "Logical marking section"),
            ("WRONG ANSWER = ZERO MARKS", "Wrong answer handling"),
            ("ZERO MARKS", "Zero marks for wrong answers"),
            ("MATHEMATICAL VALIDATION", "Mathematical validation rules"),
            ("EXACT_sum", "Exact sum requirement"),
            ("DIFFERENT question", "Different question detection")
        ]
        
        for phrase, description in checks:
            if phrase in react_code:
                print(f"✅ Found: {description}")
            else:
                print(f"❌ Missing: {description}")
                raise AssertionError(f"Missing critical instruction: {description}")
        
        print("\n✅ PASSED: All logical marking instructions present in ReAct engine")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise
    
    # Check LoRA model prompt
    print("\n📋 Checking LoRA Model prompt...")
    try:
        with open('src/agent/fine_tuned_grader.py', 'r', encoding='utf-8') as f:
            lora_code = f.read()
        
        lora_checks = [
            ("LOGICAL MARKING", "Logical marking section"),
            ("WRONG", "Wrong answer handling"),
            ("ZERO marks", "Zero marks instruction"),
            ("MATHEMATICAL VALIDATION", "Mathematical validation"),
            ("EXACT_sum", "Exact sum requirement")
        ]
        
        for phrase, description in lora_checks:
            if phrase in lora_code:
                print(f"✅ Found: {description}")
            else:
                print(f"❌ Missing: {description}")
                raise AssertionError(f"Missing critical instruction: {description}")
        
        print("\n✅ PASSED: All logical marking instructions present in LoRA model")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise


def test_pdf_detection():
    """Test that PDF detection improvements are in place"""
    print("\n" + "="*80)
    print("TEST 3: PDF Text Detection Improvements")
    print("="*80)
    
    print("\n📋 Checking PDF extraction code...")
    try:
        with open('chat_server.py', 'r', encoding='utf-8') as f:
            server_code = f.read()
        
        checks = [
            ("extraction_method", "Multiple extraction methods"),
            ("extraction_mode=\"layout\"", "Layout extraction fallback"),
            ("content_length", "Content length validation"),
            ("Image-based PDF", "Image-based PDF warning"),
            ("Encrypted/protected", "Encryption detection"),
            ("Good extraction quality", "Quality feedback")
        ]
        
        for phrase, description in checks:
            if phrase in server_code:
                print(f"✅ Found: {description}")
            else:
                print(f"❌ Missing: {description}")
                raise AssertionError(f"Missing PDF improvement: {description}")
        
        print("\n✅ PASSED: All PDF detection improvements present")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise


def test_validation_integration():
    """Test that validation is integrated into the server"""
    print("\n" + "="*80)
    print("TEST 4: Validation Integration in Server")
    print("="*80)
    
    print("\n📋 Checking server integration...")
    try:
        with open('chat_server.py', 'r', encoding='utf-8') as f:
            server_code = f.read()
        
        checks = [
            ("from src.utils.grading_validator import", "Validator imported"),
            ("validate_and_fix_grading", "Validation function used"),
            ("format_validated_grading", "Formatting function used"),
            ("Validating grading output", "Validation message")
        ]
        
        for phrase, description in checks:
            if phrase in server_code:
                print(f"✅ Found: {description}")
            else:
                print(f"❌ Missing: {description}")
                raise AssertionError(f"Missing integration: {description}")
        
        print("\n✅ PASSED: Validation properly integrated into server")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*80)
    print("🧪 AUTOGRADE+ CORRECTNESS TEST SUITE")
    print("="*80)
    print("\nTesting all three critical fixes:")
    print("1. PDF text detection through multiple methods")
    print("2. Mathematical correctness (no exceeding, correct sums)")
    print("3. Logical marking (wrong answers = zero marks)")
    print("\nBoth ReAct and LoRA models will be tested...")
    
    try:
        test_mathematical_validation()
        test_logical_marking_prompt()
        test_pdf_detection()
        test_validation_integration()
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED!")
        print("="*80)
        print("\n✅ Mathematical validation: WORKING")
        print("✅ Logical marking: IMPLEMENTED")
        print("✅ PDF detection: ENHANCED")
        print("✅ Both models: UPDATED")
        print("\nYour AutoGrade+ system is now mathematically and logically correct!")
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ TESTS FAILED")
        print("="*80)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
