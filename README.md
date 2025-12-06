# AutoGrade+ | AI-Powered Grading Assistant

A modern, ChatGPT-style web interface for automated grading using AI. Upload questions, rubrics, and student answers to get instant, detailed feedback.

![AutoGrade+ Interface](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)

## ✨ Features

### 🎨 ChatGPT-Style Interface
- Modern dark theme with smooth animations
- Real-time chat interactions
- Message history and session management
- Premium design with glassmorphism effects

### 📁 Smart File Upload
- **Plus icon** for easy file selection
- Support for PDF, TXT, and CSV files
- Automatic file categorization
- Drag-and-drop support

### 🤖 AI-Powered Grading
- Automatic extraction of questions, rubrics, and student answers
- Detailed feedback with scoring
- Support for Groq and Ollama models
- Intelligent content parsing

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python chat_server.py
```

The server will start at `http://localhost:5000`

### 3. Open in Browser

Navigate to `http://localhost:5000` and you'll see the ChatGPT-style interface.

### 4. Configure API Key

1. In the sidebar, enter your Groq API key
2. Select your model provider (Groq or Ollama)
3. Settings are automatically saved in browser

## 📖 How to Use

### Method 1: Upload Named Files

Name your files with keywords for automatic detection:
- `assignment1_rubric.pdf` → Detected as rubric
- `question_week3.txt` → Detected as question
- `student_answer_john.pdf` → Detected as answer

### Method 2: Upload Any 2 PDFs

1. Upload your first PDF (contains question and rubric)
2. Upload your second PDF (contains student answer)
3. Type: "First PDF has question and rubric, second is student answer"
4. Press Enter

The system will automatically:
- Extract text from both PDFs
- Categorize the content
- Grade the submission
- Provide detailed feedback

## 📂 Project Structure

```
Project_i222371/
├── frontend/              # ChatGPT-style interface
│   ├── index.html        # Main HTML
│   ├── styles.css        # Premium dark theme
│   ├── app.js            # Frontend logic
│   └── README.md         # Frontend docs
├── src/
│   ├── agent/
│   │   └── react_engine.py   # Grading agent
│   └── utils/
│       └── file_loader.py    # File extraction
├── chat_server.py        # Flask backend (MAIN SERVER)
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🛠️ Technologies

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Flask, Python 3.12
- **AI**: LangChain, Groq, Ollama
- **PDF Processing**: pypdf
- **Design**: Modern dark theme with animations

## 🎯 Key Features Explained

### Intelligent File Detection

The system automatically detects file types based on:
1. **Filename keywords**: rubric, question, answer, student
2. **User instructions**: Tell the system which file is which
3. **Smart defaults**: First PDF = question+rubric, Second PDF = answer

### Automatic Grading

Once all required files are uploaded:
- ✅ Question detected
- ✅ Rubric detected
- ✅ Student answer detected

The AI automatically grades and provides:
- **Numerical score** (e.g., 7/10)
- **Detailed feedback** by rubric criteria
- **Suggestions** for improvement

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Ensure Flask is installed
pip install flask flask-cors pypdf

# Check if port 5000 is available
# On Windows, close other apps using port 5000
```

### Files Not Uploading
- Check file size (large PDFs may take time)
- Ensure file types are supported (PDF, TXT, CSV)
- Check browser console for errors (F12)

### Grading Not Working
- Verify API key is entered correctly
- Check internet connection (for Groq)
- Ensure all three components are uploaded

### Windows Transformers Error
Already fixed! The encoding issue has been resolved in `src/agent/react_engine.py`

## 📝 Example Usage

1. **Start the server**: `python chat_server.py`
2. **Open browser**: `http://localhost:5000`
3. **Upload files**:
   - Click the **+** icon
   - Select your PDFs
4. **Get results**: Automatic grading with detailed feedback

## 🔑 Getting a Groq API Key

1. Visit [https://groq.com](https://groq.com)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into the sidebar settings

## 📊 Supported File Formats

| Format | Use Case | Example |
|--------|----------|---------|
| PDF | Questions, rubrics, answers | `assignment.pdf` |
| TXT | Plain text submissions | `answer.txt` |
| CSV | Structured rubrics | `rubric.csv` |

## 🎓 Project Context

This is part of the **AutoGrade+** project for GenAI coursework, comparing:
1. **ReAct Agent** - Using LangChain with reasoning
2. **LoRA Fine-Tuned Model** - Custom fine-tuned grading model

## 📄 License

Part of the AutoGrade+ project for academic purposes.

## 🤝 Contributing

This is an academic project. For questions or issues, please contact the project maintainer.

---

**Made with ❤️ for automated grading**
