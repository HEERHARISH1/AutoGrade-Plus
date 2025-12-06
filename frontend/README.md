# AutoGrade+ ChatGPT-Style Frontend

A modern, ChatGPT-like web interface for the AutoGrade+ AI grading system.

## Features

✨ **ChatGPT-Style Interface**
- Modern dark theme with smooth animations
- Real-time chat interactions
- Message history and session management

📁 **Smart File Upload**
- Plus icon for easy file uploads
- Support for PDF, TXT, and CSV files
- Automatic file type detection
- Drag-and-drop support

🤖 **Intelligent Grading**
- Automatic extraction of questions, rubrics, and student answers
- AI-powered grading with detailed feedback
- Integration with Groq and Ollama models

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python chat_server.py
```

The server will start at `http://localhost:5000`

### 3. Configure API Key

1. Open the web interface at `http://localhost:5000`
2. In the sidebar settings panel, enter your Groq API key
3. Select your preferred model provider (Groq or Ollama)

## Usage

### Uploading Files

1. Click the **+** icon in the input area
2. Select your files (PDF, TXT, or CSV)
3. Files are automatically categorized:
   - Files with "rubric" in the name → Rubric
   - Files with "question" in the name → Question
   - Files with "answer" or "student" in the name → Student Answer

### Grading a Submission

**Option 1: Upload Files**
1. Upload rubric file (e.g., `rubric.pdf`)
2. Upload question file (e.g., `question.txt`)
3. Upload student answer (e.g., `student_answer.txt`)
4. The system will automatically grade the submission

**Option 2: Paste Content**
1. Type or paste the question, rubric, and answer in the chat
2. Ask the system to grade the submission

### Example File Names

For automatic detection, name your files like:
- `assignment1_rubric.pdf`
- `question_week3.txt`
- `student_answer_john.txt`

## File Structure

```
Project_i222371/
├── frontend/
│   ├── index.html      # Main HTML interface
│   ├── styles.css      # Premium dark theme styling
│   └── app.js          # Frontend JavaScript logic
├── chat_server.py      # Flask backend API
├── app.py              # Original Streamlit app
└── src/
    └── agent/
        └── react_engine.py  # Grading agent
```

## API Endpoints

### POST /api/chat
Send a message and/or files for processing

**Request:**
```json
{
  "message": "Grade this submission",
  "files": [...],
  "api_key": "your-groq-api-key",
  "model_provider": "groq"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Grading result...",
  "extracted_files": ["rubric", "question", "answer"]
}
```

### POST /api/upload
Upload and extract files

### POST /api/grade
Grade a submission with provided question, rubric, and answer

## Troubleshooting

### Windows Transformers Error

If you encounter `OSError: [Errno 22] Invalid argument` on Windows:

The fix has been applied in `src/agent/react_engine.py`:
```python
if sys.platform == 'win32':
    import locale
    locale.getpreferredencoding = lambda: "UTF-8"
```

### Backend Not Available

If the Flask server is not running, the frontend will use simulated responses. Start the server with:
```bash
python chat_server.py
```

### API Key Issues

Make sure to:
1. Enter your Groq API key in the settings panel
2. Get a free API key at https://groq.com
3. The key is saved in browser localStorage

## Technologies Used

- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Flask, Python
- **AI:** LangChain, Groq, Ollama
- **Design:** Modern dark theme with glassmorphism

## License

Part of the AutoGrade+ project for GenAI coursework.
