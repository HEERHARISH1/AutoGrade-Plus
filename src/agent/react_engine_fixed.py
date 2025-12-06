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
        """Loads a rubric into the tool."""
        self.rubric_parser.parse_text(rubric_text)

    def grade_submission(self, question, student_answer):
        """Runs the agent to grade the submission using direct LLM call."""
        
        # Get rubric details
        rubric_desc = self.rubric_parser.get_criteria_tool_desc()
        
        # Create prompt
        prompt_template = """You are an expert grader. Grade the following student answer based on the rubric below.

RUBRIC:
{rubric}

QUESTION: {question}

STUDENT ANSWER: {student_answer}

TASK:
1. Carefully read the rubric criteria.
2. Evaluate the student's answer against each criterion.
3. Assign points for each criterion based on how well the answer meets it.
4. Provide detailed, constructive feedback.

Respond in this EXACT JSON format (no extra text):
{{
  "score": <total_numeric_score>,
  "max_score": <total_possible_points>,
  "feedback": "<detailed_explanation_of_grading>",
  "breakdown": {{
    "<criterion_name>": {{"points": <points_awarded>, "max": <max_points>, "comment": "<brief_comment>"}},
    ...
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
            response = self.llm.invoke(formatted_prompt)
            
            # Extract content
            if hasattr(response, 'content'):
                output = response.content
            else:
                output = str(response)
            
            return {
                "output": output,
                "input": formatted_prompt
            }
        except Exception as e:
            return {
                "output": f"Error during grading: {str(e)}",
                "input": formatted_prompt
            }
