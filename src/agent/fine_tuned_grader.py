"""
Fine-tuned model integration for AutoGrade+
This module loads and uses the LoRA fine-tuned model
"""

import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class FineTunedGrader:
    """Grading using the fine-tuned LoRA model"""
    
    def __init__(self, model_path="lora_model"):
        """
        Initialize the fine-tuned model
        
        Args:
            model_path: Path to the saved LoRA model directory
        """
        print(f"Loading fine-tuned model from {model_path}...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        print("✅ Fine-tuned model loaded successfully!")
    
    def grade_submission(self, question, rubric, student_answer):
        """
        Grade a submission using the fine-tuned model
        
        Returns:
            dict with 'output' containing the JSON grading result
        """
        # Format prompt in Alpaca style with STRICT grading rules
        prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
You are an EXPERT GRADER. Grade the submission based on the rubric with STRICT ACCURACY.

CRITICAL RULES:
1. **LOGICAL MARKING:** If answer is WRONG or addresses a different question → ZERO marks with explanation
2. **MATHEMATICAL VALIDATION:** 
   - Each criterion's points MUST be <= max points
   - Final score MUST EXACTLY equal sum of all breakdown points
   - Verify: score = sum(all breakdown points)
3. **CORRECTNESS ONLY:** Award points ONLY for correct answers, NOT for effort or length

### Input:
QUESTION:
{question}

RUBRIC:
{rubric}

STUDENT ANSWER:
{student_answer}

### Response:
Respond in EXACT JSON format (no extra text):
{{
  "score": <EXACT_sum_of_breakdown_points>,
  "max_score": <total_max_points>,
  "feedback": "<mention if wrong/correct, explain why>",
  "breakdown": {{
    "<criterion>": {{"points": <awarded_<=_max>, "max": <max>, "comment": "<specific justification>"}},
    ...
  }}
}}
"""
        
        # Tokenize and generate
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.1,
                do_sample=True,
                top_p=0.9
            )
        
        # Decode output
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the response part (after "### Response:")
        if "### Response:" in response:
            output = response.split("### Response:")[-1].strip()
        else:
            output = response
        
        return {
            "output": output,
            "input": prompt
        }
