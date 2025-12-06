import os
import json
import random
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Initialize LLM
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

llm = ChatGroq(temperature=0.7, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")

def generate_synthetic_example(topic, difficulty="intermediate"):
    """
    Generates a synthetic training example: Question, Rubric, Student Answer, and the Ideal Grade.
    """
    print(f"🎨 Generating content for topic: {topic} ({difficulty})...")
    
    # 1. Generate Question
    question_prompt = f"""Write a university-level assignment question for the topic: '{topic}'. 
Difficulty: {difficulty}. Keep it concise (2-3 sentences). Output ONLY the question text, no extra formatting."""
    
    question = llm.invoke(question_prompt).content.strip()
    
    # 2. Generate Rubric
    rubric_prompt = f"""Create a grading rubric for this question: "{question}"
Total points: 10. List 3-4 criteria with point values. Keep it simple and clear. Output ONLY the rubric text."""
    
    rubric = llm.invoke(rubric_prompt).content.strip()
    
    # 3. Generate a Student Answer
    quality = random.choice(["excellent", "average", "poor"])
    print(f"   ✍️  Writing a {quality} student answer...")
    
    answer_prompt = f"""Write a {quality} quality student answer for: "{question}"
Keep it 3-5 sentences. Output ONLY the answer text."""
    
    student_answer = llm.invoke(answer_prompt).content.strip()

    # 4. Grade the Answer
    print(f"   ⚖️  Grading the submission...")
    grading_prompt = f"""Grade this submission. Output ONLY valid JSON, no markdown.

RUBRIC: {rubric}
QUESTION: {question}
ANSWER: {student_answer}

JSON format:
{{"score": <number>, "max_score": 10, "feedback": "<one sentence>", "breakdown": {{"criterion1": {{"points": <num>, "max": <num>, "comment": "<short>"}}}}}}"""
    
    grade_response = llm.invoke(grading_prompt).content.strip()
    
    # Extract and validate JSON
    try:
        import re
        # Remove any markdown
        grade_response = re.sub(r'```\w*\s*', '', grade_response)
        # Find JSON
        match = re.search(r'\{.+\}', grade_response, re.DOTALL)
        if match:
            grade_json = match.group(0)
            # Validate
            json.loads(grade_json)
        else:
            raise ValueError("No JSON found")
            
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return None

    return {
        "instruction": "Grade the following submission based on the provided rubric.",
        "input": f"QUESTION:\n{question}\n\nRUBRIC:\n{rubric}\n\nSTUDENT ANSWER:\n{student_answer}",
        "output": grade_json
    }

def main():
    topics = [
        # Computer Science
        "Python Recursion",
        "Object-Oriented Programming",
        "Binary Search Trees",
        "Database Normalization",
        "REST API Design",
        
        # History
        "The Causes of WWI",
        "The French Revolution",
        "The Cold War",
        "Ancient Roman Empire",
        "The Industrial Revolution",
        
        # Science
        "Photosynthesis Process",
        "Newton's Laws of Motion",
        "DNA Replication",
        "Chemical Bonding",
        "The Water Cycle",
        
        # Economics
        "Supply and Demand Economics",
        "Monetary Policy",
        "Market Structures",
        "Fiscal Policy",
        "Opportunity Cost",
        
        # Literature
        "Literary Analysis of Hamlet",
        "Symbolism in The Great Gatsby",
        "Themes in 1984",
        "Character Development in Pride and Prejudice",
        "Narrative Structure in To Kill a Mockingbird",
        
        # Mathematics
        "Calculus Derivatives",
        "Linear Algebra Matrices",
        "Probability Theory",
        "Statistics Hypothesis Testing",
        "Trigonometric Functions"
    ]
    
    dataset = []
    
    print("🚀 Starting Synthetic Data Generation...")
    print(f"📊 Target: {len(topics)} examples\n")
    
    for i, topic in enumerate(topics, 1):
        print(f"[{i}/{len(topics)}] ", end="")
        example = generate_synthetic_example(topic)
        if example:
            dataset.append(example)
            print("   ✅ Example generated successfully!\n")
        else:
            print("   ⚠️  Skipped due to error\n")
            
    # Save to JSONL
    output_file = "training_data.jsonl"
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in dataset:
            f.write(json.dumps(entry) + '\n')
            
    print(f"🎉 Generated {len(dataset)}/{len(topics)} examples. Saved to {output_file}")

if __name__ == "__main__":
    main()
