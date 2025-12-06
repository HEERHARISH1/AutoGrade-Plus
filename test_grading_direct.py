"""
Direct test of the grading agent to see what output we get
"""
import sys
import os
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, 'c:/Users/heerh/OneDrive/Desktop/FAST/7th_Semester/GenAI/Project_i222371')

from dotenv import load_dotenv
load_dotenv()

from src.agent.react_engine import GradingAgent

# Get API key
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    print("❌ No GROQ_API_KEY found in environment")
    sys.exit(1)

print("✅ API Key found")
print(f"Key preview: {api_key[:10]}...")

# Read test files
with open('Test_Samples/question.txt', 'r') as f:
    question = f.read()

with open('Test_Samples/rubric.txt', 'r') as f:
    rubric = f.read()
    
with open('Test_Samples/student_answer.py', 'r') as f:
    answer = f.read()

print("\n" + "="*80)
print("📚 TEST DATA LOADED")
print("="*80)
print(f"Question length: {len(question)} chars")
print(f"Rubric length: {len(rubric)} chars")
print(f"Answer length: {len(answer)} chars")

# Create agent
print("\n" + "="*80)
print("🤖 CREATING GRADING AGENT")
print("="*80)

try:
    agent = GradingAgent(model_provider="groq", api_key=api_key)
    print("✅ Agent created successfully")
except Exception as e:
    print(f"❌ Failed to create agent: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Load rubric
print("\n" + "="*80)
print("📋 LOADING RUBRIC")
print("="*80)
agent.load_rubric(rubric)
print("✅ Rubric loaded")

# Grade submission
print("\n" + "="*80)
print("🎓 GRADING SUBMISSION")
print("="*80)

try:
    result = agent.grade_submission(question, answer)
    
    print("\n" + "="*80)
    print("📊 GRADING RESULT")
    print("="*80)
    print(f"\nOutput length: {len(result['output'])} chars")
    print("\nFirst 500 chars of output:")
    print("-" * 80)
    print(result['output'][:500])
    print("-" * 80)
    
    if len(result['output']) > 500:
        print(f"\n... (truncated, showing first 500 of {len(result['output'])} chars)")
    
    # Try to validate
    print("\n" + "="*80)
    print("✅ VALIDATING OUTPUT")
    print("="*80)
    
    from src.utils.grading_validator import validate_and_fix_grading
    validated = validate_and_fix_grading(result['output'])
    
    print(f"\nValidated score: {validated.get('score', 'N/A')} / {validated.get('max_score', 'N/A')}")
    print(f"Feedback: {validated.get('feedback', 'N/A')[:100]}...")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("✅ TEST COMPLETE")
print("="*80)
