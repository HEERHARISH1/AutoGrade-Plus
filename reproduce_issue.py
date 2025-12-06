import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import io

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

# Read files
with open('Test_Samples/question.txt', 'r') as f:
    question = f.read()
with open('Test_Samples/rubric.txt', 'r') as f:
    rubric_text = f.read()
with open('Test_Samples/student_answer.py', 'r') as f:
    answer = f.read()

print("Files loaded.")

# Initialize LLM
api_key = os.getenv('GROQ_API_KEY')
llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")

# 1. Extract Rubric (Simulate load_rubric)
print("Extracting rubric...")
rubric_prompt = f"""Extract the grading criteria from the following text.
RUBRIC TEXT:
{rubric_text[:4000]}
Output ONLY a simple list of criteria."""

try:
    rubric_desc = llm.invoke(rubric_prompt).content
    print(f"Rubric extracted ({len(rubric_desc)} chars).")
except Exception as e:
    print(f"Rubric extraction failed: {e}")
    rubric_desc = rubric_text

# 2. Grade Submission (Simulate grade_submission)
print("Grading submission...")
prompt_template = """You are an EXPERT GRADER...
RUBRIC:
{rubric}

QUESTION: {question}

STUDENT ANSWER: {student_answer}

⚠️ CRITICAL OUTPUT FORMAT:
- Output ONLY valid JSON
- NO markdown code blocks
- NO extra text

Respond in this EXACT JSON format:
{{
  "score": <number>,
  "max_score": <number>,
  "feedback": "<text>",
  "breakdown": {{ ... }}
}}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["rubric", "question", "student_answer"]
)

formatted_prompt = prompt.format(
    rubric=rubric_desc,
    question=question,
    student_answer=answer
)

try:
    print("Invoking LLM for grading...")
    response = llm.invoke(formatted_prompt)
    output = response.content
    
    print("\n" + "="*40)
    print("RAW OUTPUT FROM LLM:")
    print("="*40)
    print(output)
    print("="*40)
    
    # Try to parse it
    import json
    import re
    
    # Use my new extraction logic
    print("\nAttempting extraction...")
    text = re.sub(r'```json\s*', '', output)
    text = re.sub(r'```\s*', '', text)
    match = re.search(r'\{.*\}', text, re.DOTALL)
    
    if match:
        json_str = match.group(0)
        print("JSON candidate found.")
        try:
            data = json.loads(json_str)
            print("✅ JSON PARSED SUCCESSFULLY!")
            print(f"Score: {data.get('score')}")
        except Exception as e:
            print(f"❌ JSON PARSE ERROR: {e}")
    else:
        print("❌ NO JSON FOUND IN OUTPUT")

except Exception as e:
    print(f"❌ EXECUTION ERROR: {e}")
