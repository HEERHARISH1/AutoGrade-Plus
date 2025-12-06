from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix for Windows transformers issue
if sys.platform == 'win32':
    import locale
    locale.getpreferredencoding = lambda: "UTF-8"

from src.agent.react_engine import GradingAgent

app = Flask(__name__, static_folder='frontend')
CORS(app)

# Global API Key from environment
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Get form data
        message = request.form.get('message', '')
        # Use server-side API key if not provided (though frontend won't send it anymore)
        api_key = request.form.get('api_key') or GROQ_API_KEY
        model_provider = request.form.get('model_provider', 'groq')
        
        if not api_key and model_provider == 'groq':
             return jsonify({'success': False, 'error': 'Server configuration error: Groq API Key not found.'}), 500

        # Process uploaded files if any
        files_content = {}
        file_names = []
        
        if 'files' in request.files:
            files = request.files.getlist('files')
            print(f"\n📦 Processing {len(files)} uploaded file(s)...")
            for file in files:
                filename = file.filename
                file_names.append(filename)
                
                # Save temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                    file.save(tmp.name)
                    tmp_path = tmp.name
                
                # Extract content based on file type
                try:
                    filename_lower = filename.lower()
                    if filename_lower.endswith('.pdf'):
                        # Enhanced PDF extraction with multiple methods
                        try:
                            import pypdf
                            content = ''
                            extraction_method = 'standard'
                            
                            with open(tmp_path, 'rb') as f:
                                pdf_reader = pypdf.PdfReader(f)
                                num_pages = len(pdf_reader.pages)
                                
                                print(f"📄 Extracting {num_pages} pages from {filename}...")
                                
                                for page_num, page in enumerate(pdf_reader.pages):
                                    try:
                                        # Try standard extraction first
                                        page_text = page.extract_text()
                                        
                                        # If extraction is poor, try alternative method
                                        if len(page_text.strip()) < 50:
                                            try:
                                                # Try with layout preservation
                                                page_text = page.extract_text(extraction_mode="layout")
                                                extraction_method = 'layout'
                                            except:
                                                pass
                                        
                                        content += page_text + '\n'
                                        
                                    except Exception as page_error:
                                        print(f"⚠️ Page {page_num + 1} extraction warning: {page_error}")
                                        content += f"[Page {page_num + 1} extraction issue]\n"
                                
                                # Validate extraction quality
                                content_length = len(content.strip())
                                log_msg = f"✅ Extracted {content_length} characters from {filename} using {extraction_method} method"
                                print(log_msg)
                                
                                # Log to file for debugging
                                try:
                                    with open('extraction_log.txt', 'a', encoding='utf-8') as logf:
                                        logf.write(f"{log_msg}\n")
                                        if content_length > 0:
                                            logf.write(f"Preview: {content[:200]}\n")
                                        else:
                                            logf.write("Preview: [EMPTY]\n")
                                        logf.write("-" * 50 + "\n")
                                except Exception as log_err:
                                    print(f"Logging failed: {log_err}")

                                # Check if we got meaningful content
                                
                                # Check if we got meaningful content
                                if content_length < 100:
                                    warning_msg = (
                                        f"⚠️ WARNING: PDF '{filename}' yielded only {content_length} characters.\n"
                                        f"This may indicate:\n"
                                        f"  - Image-based PDF (scanned document)\n"
                                        f"  - Encrypted/protected PDF\n"
                                        f"  - Empty or corrupted PDF\n"
                                        f"Extracted content: {content[:200]}\n"
                                    )
                                    print(warning_msg)
                                    content = warning_msg + "\n\n" + content
                                elif content_length < 500:
                                    print(f"⚠️ Low text content ({content_length} chars) - may be incomplete")
                                else:
                                    print(f"✅ Good extraction quality ({content_length} characters)")
                                    
                        except Exception as pdf_error:
                            content = (
                                f"[PDF extraction error: {str(pdf_error)}]\n"
                                f"Please ensure the PDF:\n"
                                f"  - Is not password-protected or encrypted\n"
                                f"  - Contains actual text (not just images)\n"
                                f"  - Is not corrupted\n"
                            )
                            print(f"❌ PDF error for {filename}: {pdf_error}")
                            
                    elif filename_lower.endswith('.csv'):
                        with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        print(f"✅ Extracted {len(content)} chars from CSV: {filename}")
                    elif filename_lower.endswith(('.txt', '.py', '.md', '.json')):
                        with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        print(f"✅ Extracted {len(content)} chars from {filename}")
                        print(f"   Preview: {content[:100]}")
                    else:
                        # Try to read as text with error handling
                        try:
                            with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            print(f"✅ Extracted {len(content)} chars from {filename}")
                        except Exception:
                            content = f"[Could not read file {filename} - unsupported format]"
                            print(f"❌ Failed to read {filename}")
                    
                    files_content[filename] = content
                    print(f"📦 Added '{filename}' to files_content ({len(content)} chars)")
                        
                finally:
                    os.unlink(tmp_path)
        
        # Use AI to intelligently categorize files
        if files_content:
            from src.utils.content_analyzer import smart_categorize_files
            uploaded_content = smart_categorize_files(files_content, api_key, model_provider)
        else:
            uploaded_content = {}
        
        # Determine response based on content
        response_text = generate_response(message, uploaded_content, api_key, model_provider, file_names)
        
        return jsonify({
            'success': True,
            'response': response_text,
            'extracted_files': list(uploaded_content.keys())
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in /api/chat: {error_details}")
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_details
        }), 500

def generate_response(message, uploaded_content, api_key, model_provider, file_names=[]):
    """Generate intelligent response based on message and uploaded files"""
    
    # Check if we have all required components for grading
    # The new smart_categorize_files splits everything into these 3 keys
    has_rubric = bool(uploaded_content.get('rubric'))
    has_question = bool(uploaded_content.get('question'))
    has_answer = bool(uploaded_content.get('answer'))
    
    # Check if all components are ready for grading
    if has_rubric and has_question and has_answer:
        # Perform grading
        try:
            # Check if user wants to use fine-tuned model
            use_finetuned = model_provider == 'finetuned'
            
            if use_finetuned:
                # Use fine-tuned model (if available)
                try:
                    from src.agent.fine_tuned_grader import FineTunedGrader
                    grader = FineTunedGrader()
                    result = grader.grade_submission(
                        str(uploaded_content['question']),
                        str(uploaded_content['rubric']),
                        str(uploaded_content['answer'])
                    )
                except Exception as ft_error:
                    return f"❌ **Fine-tuned model not available:** {str(ft_error)}\n\nPlease use 'groq' or 'ollama' model provider."
            else:
                # Use standard ReAct agent
                agent = GradingAgent(model_provider=model_provider, api_key=api_key)
                agent.load_rubric(str(uploaded_content['rubric']))
                
                result = agent.grade_submission(
                    str(uploaded_content['question']),
                    str(uploaded_content['answer'])
                )
            
            # CRITICAL: Validate and fix grading output for mathematical correctness
            from src.utils.grading_validator import validate_and_fix_grading, format_validated_grading
            
            print("\n🔍 Validating grading output for mathematical correctness...")
            validated_result = validate_and_fix_grading(result['output'])
            
            # Format the validated output nicely
            formatted_report = format_validated_grading(validated_result)
            
            model_name = "Fine-Tuned LoRA Model" if use_finetuned else f"ReAct Agent ({model_provider.title()})"
            return f"✅ **Grading Complete!** (Model: {model_name})\n\n{formatted_report}"
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Grading error: {error_trace}")
            return f"❌ **Grading Error:** {str(e)}\n\nPlease check your API key and model settings, then try again."

    
    elif uploaded_content:
        # Files uploaded but not all required components detected
        response = "📋 **Files Received:**\n\n"
        for idx, name in enumerate(file_names, 1):
            response += f"{idx}. `{name}`\n"
        
        response += "\n🤖 **AI Analysis Results:**\n"
        
        if has_question: response += "- ✅ **Question** detected\n"
        if has_rubric: response += "- ✅ **Rubric** detected\n"
        if has_answer: response += "- ✅ **Student Answer** detected\n"
        
        response += "\n⚠️ **Status Check:**\n"
        if not has_rubric: response += "- ❌ **Rubric** missing\n"
        if not has_question: response += "- ❌ **Question** missing\n"
        if not has_answer: response += "- ❌ **Student Answer** missing\n"
        
        # Provide helpful guidance
        if has_rubric and has_question and not has_answer:
            response += "\n💡 **Next Step:** Upload the student's answer file to start grading!"
        elif has_answer and not (has_rubric and has_question):
            response += "\n💡 **Next Step:** Upload the question and rubric files."
        elif not has_rubric and not has_question and not has_answer:
            response += "\n💡 **Tip:** I couldn't clearly identify the content. Please make sure your files contain clear text."
        
        return response
    
    else:
        # Just a message, no files - handle conversationally
        message_lower = message.lower().strip()
        
        # Check if it's a greeting or simple query
        greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        help_queries = ['help', 'how', 'what can you', 'what do you', 'guide', 'instructions']
        
        if any(greeting in message_lower for greeting in greetings):
            return """👋 **Hello! I'm AutoGrade+, your AI grading assistant!**

I can help you grade student assignments automatically. Here's how:

**📤 Upload Files:**
- **Option 1:** Upload all 3 components separately (question, rubric, answer)
- **Option 2:** Upload 2 files (one with question+rubric, one with answer)
- **Option 3:** Upload 1 file with everything (I'll extract what I can)

**🤖 Supported Formats:**
- PDF, TXT, CSV, Python files (.py)

**⚙️ Available Models:**
- **Groq** (ReAct Agent) - Fast and accurate
- **Ollama** (Local ReAct) - Runs locally
- **Fine-tuned** (LoRA Model) - Custom trained model

Just upload your files and I'll handle the rest! 🚀"""

        elif any(query in message_lower for query in help_queries):
            return """📚 **How to Use AutoGrade+:**

**Step 1:** Configure your settings in the sidebar
- Enter your Groq API key (get one free at groq.com)
- Select your preferred model (Groq/Ollama/Fine-tuned)

**Step 2:** Upload your files (click the + icon)
- Question file (assignment description)
- Rubric file (grading criteria)
- Student answer file (submission to grade)

**Step 3:** I'll automatically:
- Detect what each file contains using AI
- Extract text from PDFs
- Grade the submission based on the rubric
- Provide detailed feedback

**💡 Pro Tips:**
- You can upload files in any order
- Files can be combined (e.g., question+rubric in one PDF)
- I support multiple file formats (PDF, TXT, CSV, .py)

Ready to start? Upload your files! 📁"""

        elif 'grade' in message_lower or 'mark' in message_lower or 'evaluate' in message_lower:
            return """📝 **Ready to Grade!**

To grade an assignment, I need three things:

1. **Question/Assignment** - What was the task?
2. **Rubric** - How should it be graded?
3. **Student Answer** - What did the student submit?

**Upload your files and I'll:**
- ✅ Automatically detect what each file contains
- ✅ Extract text from PDFs
- ✅ Grade based on the rubric
- ✅ Provide detailed feedback with scores

Click the **+** icon to upload files! 📤"""

        else:
            # Off-topic or complex query
            return f"""🤖 **I'm AutoGrade+, specialized for grading assignments.**

I noticed you asked: *"{message}"*

While I'm designed specifically for automated grading, I can help you with:
- ✅ Grading student submissions
- ✅ Evaluating answers against rubrics
- ✅ Providing detailed feedback
- ✅ Scoring assignments

**To get started with grading:**
Upload your question, rubric, and student answer files (click the + icon).

If you have a different question, I recommend using a general-purpose AI assistant. My specialty is grading! 📝"""



def format_grading_output(raw_output):
    """Parses JSON output and formats it into a nice Markdown report"""
    try:
        import json
        import re
        
        # Extract JSON if wrapped in code blocks
        json_str = raw_output
        match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if match:
            json_str = match.group(0)
            
        data = json.loads(json_str)
        
        # Build Markdown Report
        md = f"### 🎓 **Final Score: {data.get('score', 0)} / {data.get('max_score', 10)}**\n\n"
        
        md += f"#### 📝 **Feedback Summary**\n"
        md += f"{data.get('feedback', 'No feedback provided.')}\n\n"
        
        md += f"#### 📊 **Detailed Breakdown**\n"
        md += "| Criterion | Score | Comments |\n"
        md += "| :--- | :---: | :--- |\n"
        
        breakdown = data.get('breakdown', {})
        for criterion, details in breakdown.items():
            points = details.get('points', 0)
            max_pts = details.get('max', 0)
            comment = details.get('comment', '')
            md += f"| **{criterion}** | {points}/{max_pts} | {comment} |\n"
            
        return md
        
    except Exception as e:
        # If parsing fails, return raw output but try to clean it up
        print(f"Formatting error: {e}")
        return raw_output

if __name__ == '__main__':
    print("🚀 Starting AutoGrade+ Server...")
    print("📱 Frontend: http://localhost:5000")
    print("🔌 API: http://localhost:5000/api")
    app.run(debug=True, port=5000)
