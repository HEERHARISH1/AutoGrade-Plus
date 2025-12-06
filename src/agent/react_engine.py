import os
import sys

# Fix for Windows transformers issue - set encoding before import
if sys.platform == 'win32':
    import locale
    locale.getpreferredencoding = lambda: "UTF-8"

from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatOllama
from src.agent.rubric_tool import RubricParser

class GradingAgent:
    """
    Grading Agent using direct LLM calls (compatible with LangChain 1.1.0+)
    """
    def __init__(self, model_provider="groq", model_name="llama-3.3-70b-versatile", api_key=None):
        self.rubric_parser = RubricParser()
        self.api_key = api_key
        
        # Initialize LLM
        if model_provider == "groq":
            if not api_key:
                raise ValueError("Groq API Key is required")
            self.llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name=model_name)
        elif model_provider == "ollama":
            self.llm = ChatOllama(model="llama3")
        else:
            raise ValueError("Unsupported provider. Use 'groq' or 'ollama'")

    def load_rubric(self, rubric_text):
        """Loads a rubric into the tool using LLM extraction."""
        # Use LLM to structure the rubric
        prompt = f"""Extract the grading criteria from the following text.
        
        RUBRIC TEXT:
        {rubric_text[:4000]}
        
        Output ONLY a simple list of criteria in this format:
        - [Criterion Name]: [Max Points] points. [Description]
        
        Example:
        - Grammar: 10 points. Check for spelling and syntax.
        - Logic: 20 points. Assess the validity of arguments.
        """
        
        try:
            response = self.llm.invoke(prompt)
            if hasattr(response, 'content'):
                self.rubric_desc = response.content
            else:
                self.rubric_desc = str(response)
        except Exception as e:
            print(f"Rubric extraction failed: {e}")
            self.rubric_desc = rubric_text  # Fallback to raw text

    def grade_submission(self, question, student_answer):
        """Runs the agent to grade the submission using direct LLM call."""
        
        # Use the extracted rubric description
        rubric_desc = getattr(self, 'rubric_desc', "No rubric provided.")
        
        # CRITICAL: Truncate content to avoid Error 413 (request too large)
        # Groq FREE TIER limit: 12,000 tokens per minute
        # Strategy: Prioritize answer content, keep rubric/question concise
        MAX_RUBRIC_CHARS = 4000    # ~1000 tokens - essential rubric only
        MAX_QUESTION_CHARS = 6000   # ~1500 tokens - key requirements
        MAX_ANSWER_CHARS = 16000    # ~4000 tokens - most of the answer
        # Total: ~6,500 tokens + prompt (~2K) = ~8,500 tokens (safely under 12K)
        
        if len(rubric_desc) > MAX_RUBRIC_CHARS:
            print(f"⚠️ Truncating rubric from {len(rubric_desc)} to {MAX_RUBRIC_CHARS} chars")
            rubric_desc = rubric_desc[:MAX_RUBRIC_CHARS] + "\n...[truncated]"
        
        if len(question) > MAX_QUESTION_CHARS:
            print(f"⚠️ Truncating question from {len(question)} to {MAX_QUESTION_CHARS} chars")
            question = question[:MAX_QUESTION_CHARS] + "\n...[truncated]"
        
        if len(student_answer) > MAX_ANSWER_CHARS:
            print(f"⚠️ Truncating answer from {len(student_answer)} to {MAX_ANSWER_CHARS} chars")
            student_answer = student_answer[:MAX_ANSWER_CHARS] + "\n...[truncated]"
        
        # Create prompt with SMART CONTEXT + STRICT MATH + LOGICAL MARKING
        prompt_template = """You are an EXPERT GRADER with deep understanding of educational assessment. Your job is to ACCURATELY evaluate student work based on the provided rubric.

RUBRIC:
{rubric}

QUESTION: {question}

STUDENT ANSWER: {student_answer}

⚠️ CRITICAL GRADING INSTRUCTIONS:

1. **CONTEXT AWARENESS & FAIR MARKING:**
   - Read the QUESTION to understand what was asked.
   - Read the RUBRIC to understand how to grade.
   - Read the ANSWER to see what was actually done.
   - **GRADING APPROACH:**
     * If answer is COMPLETELY WRONG or IRRELEVANT → ZERO marks
     * If answer shows SOME understanding but has errors → Give partial credit
     * If answer is MOSTLY CORRECT with minor issues → Give most points
     * If answer is FULLY CORRECT → FULL marks

2. **BALANCED GRADING:**
   - **Completely wrong/irrelevant = ZERO MARKS**
   - **Shows effort and some understanding = Partial credit (30-50%)**
   - **Mostly correct with errors = Good marks (60-80%)**
   - **Fully correct = FULL MARKS (90-100%)**
   - Be fair and recognize student effort while maintaining accuracy

3. **STRICT MATHEMATICAL VALIDATION RULES:**
   - **Rule A (No Exceeding):** Each criterion's awarded points MUST be ≤ its max points
     * Example: If max is 5, you CANNOT award 6, 7, or any value > 5
   - **Rule B (Exact Sum):** Final score MUST EXACTLY equal the sum of all breakdown points
     * Example: If breakdown is 3+2+4 = 9, then score MUST be 9, NOT 10
   - **Rule C (Double Check):** Before outputting, manually verify:
     * Sum all breakdown points: points1 + points2 + ... = ?
     * Does this sum equal the "score" field? If NO, FIX IT!
   - **Rule D (No Decimals Unless Necessary):** Use whole numbers unless rubric specifies decimals

4. **SCORING SCALE (Be Generous but Fair):**
   - **90-100%:** Excellent - correct and complete
   - **70-89%:** Good - mostly correct, minor issues
   - **50-69%:** Satisfactory - shows understanding, has errors
   - **30-49%:** Needs improvement - incomplete or significant errors
   - **0-29%:** Unsatisfactory - wrong, irrelevant, or no understanding

5. **MANDATORY VALIDATION BEFORE OUTPUT:**
   - Step 1: Calculate each criterion score (ensure <= max)
   - Step 2: Sum all criterion scores: total = sum(all breakdown points)
   - Step 3: Set "score" field = total (NOT an estimate, EXACT sum)
   - Step 4: Verify: Does score field match the sum? If NO, recalculate!

THINKING PROCESS (Do this internally):
1. For each criterion in rubric:
   a. What is being tested?
   b. Did the student answer this correctly? (Yes/No/Partial)
   c. Assign points: 0 (wrong), partial (some correct), or max (fully correct)
   d. Ensure: awarded_points <= max_points
2. Calculate total: SUM of all awarded points
3. Set score = this exact sum
4. Verify math: Does score = sum of breakdown? Must be TRUE!

⚠️ CRITICAL OUTPUT FORMAT:
- Output ONLY valid JSON
- NO markdown code blocks (no ```json or ```)
- NO extra text before or after the JSON
- NO explanations or comments outside the JSON
- Use DOUBLE QUOTES (") for all strings, NOT single quotes (')
- Ensure all braces and brackets are properly closed

Respond in this EXACT JSON format (no extra text, no markdown):
{{
  "score": <EXACT_sum_of_all_breakdown_points>,
  "max_score": <total_of_all_max_points>,
  "feedback": "<constructive feedback: mention if answer is wrong/correct, strengths, and specific areas for improvement>",
  "breakdown": {{
    "<criterion_name>": {{"points": <awarded_points_must_be_<=_max>, "max": <max_points>, "comment": "<specific justification: if wrong explain WHY, if correct explain what was good>"}},
    ...
  }}
}}

EXAMPLE VALID OUTPUT:
{{
  "score": 7,
  "max_score": 10,
  "feedback": "The answer demonstrates good understanding but has some errors in implementation.",
  "breakdown": {{
    "Correctness": {{"points": 3, "max": 5, "comment": "Logic is mostly correct but has one major error"}},
    "Code Quality": {{"points": 4, "max": 5, "comment": "Well-structured and readable code"}}
  }}
}}
"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["rubric", "question", "student_answer"]
        )
        
        # Format and invoke
        formatted_prompt = prompt.format(
            rubric=rubric_desc,
            question=question,
            student_answer=student_answer
        )
        
        try:
            print("\n" + "="*80)
            print("🤖 INVOKING LLM FOR GRADING...")
            print("="*80)
            
            response = self.llm.invoke(formatted_prompt)
            
            # Extract content
            if hasattr(response, 'content'):
                output = response.content
            else:
                output = str(response)
            
            # Debug logging
            print("\n📤 LLM RAW OUTPUT:")
            print("-" * 80)
            print(output[:1000])  # First 1000 chars
            if len(output) > 1000:
                print(f"\n... (truncated, total length: {len(output)} chars)")
            print("-" * 80)
            
            # Save to debug log for troubleshooting
            try:
                with open('debug_log.txt', 'a', encoding='utf-8') as f:
                    f.write("\n" + "=" * 80 + "\n")
                    f.write(f"TIMESTAMP: {__import__('datetime').datetime.now()}\n")
                    f.write("=" * 80 + "\n")
                    f.write("PROMPT:\n")
                    f.write(formatted_prompt[:500] + "...\n")
                    f.write("\n" + "-" * 80 + "\n")
                    f.write("RAW LLM OUTPUT:\n")
                    f.write(output)
                    f.write("\n" + "=" * 80 + "\n\n")
            except Exception as log_err:
                print(f"⚠️ Logging failed: {log_err}")
            
            return {
                "output": output,
                "input": formatted_prompt
            }
        except Exception as e:
            print(f"\n❌ LLM ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {
                "output": f"Error during grading: {str(e)}",
                "input": formatted_prompt
            }
