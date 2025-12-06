import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Force UTF-8 for Windows console
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
print(f"API Key present: {bool(api_key)}")

try:
    llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
    print("Invoking LLM...")
    response = llm.invoke("Return this exact JSON: {\"test\": \"success\"}")
    
    print("\n--- RAW OUTPUT START ---")
    print(response.content)
    print("--- RAW OUTPUT END ---")
    
except Exception as e:
    print(f"Error: {e}")
