# 🎥 Docker Demo Video - Step-by-Step Guide

## 📋 Prerequisites

### 1. Install Docker Desktop
```bash
# Download and install Docker Desktop for Windows
# Visit: https://www.docker.com/products/docker-desktop

# Or use winget:
winget install Docker.DockerDesktop
```

**After installation:**
- Restart your computer
- Open Docker Desktop
- Wait for it to start (green icon in system tray)

### 2. Verify Docker is Running
```bash
# Open PowerShell and run:
docker --version
docker-compose --version
```

You should see version numbers (e.g., Docker version 24.x.x)

---

## 🚀 Step-by-Step Demo Recording

### **STEP 1: Prepare Your Environment** (Before Recording)

#### 1.1 Stop Current Server
```bash
# Press Ctrl+C in the terminal running chat_server.py
# Or close that terminal window
```

#### 1.2 Set Your API Key
```bash
# Edit .env file
notepad .env

# Make sure it has:
GROQ_API_KEY=your_actual_api_key_here
```

#### 1.3 Clean Up (Optional)
```bash
# Remove old containers if any
docker-compose down
docker system prune -f
```

---

### **STEP 2: Start Recording** 🎬

**Recording Software Options:**
- **OBS Studio** (Free): https://obsproject.com/
- **Windows Game Bar**: Press `Win + G`
- **ShareX** (Free): https://getsharex.com/

**What to Record:**
- Your entire screen (or just browser + terminal)
- Audio (optional - you can narrate or add text)

---

### **STEP 3: Build Docker Image** (On Camera)

Open PowerShell in your project folder:

```bash
# Navigate to project
cd "c:\Users\heerh\OneDrive\Desktop\FAST\7th_Semester\GenAI\Project_i222371"

# Show the Dockerfile
type Dockerfile

# Build the Docker image
docker build -t autograde-plus .
```

**Expected Output:**
```
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition
 => => transferring dockerfile
 => [internal] load .dockerignore
 => [stage-0 1/4] FROM docker.io/library/python:3.12-slim
 => [stage-0 2/4] WORKDIR /app
 => [stage-0 3/4] COPY requirements.txt .
 => [stage-0 4/4] RUN pip install --no-cache-dir -r requirements.txt
 => exporting to image
 => => naming to docker.io/library/autograde-plus
```

**⏱️ Time**: ~2-5 minutes (depending on internet speed)

---

### **STEP 4: Run Docker Container** (On Camera)

```bash
# Start the container using docker-compose
docker-compose up
```

**Expected Output:**
```
[+] Running 1/1
 ✔ Container autograde-plus  Created
Attaching to autograde-plus
autograde-plus  | 🚀 Starting AutoGrade+ Server...
autograde-plus  | 📱 Frontend: http://localhost:5000
autograde-plus  | 🔌 API: http://localhost:5000/api
autograde-plus  |  * Running on http://127.0.0.1:5000
```

**✅ Success Indicator**: You see "Running on http://127.0.0.1:5000"

---

### **STEP 5: Open Browser and Demo** (On Camera)

#### 5.1 Open Application
```bash
# In browser, go to:
http://localhost:5000
```

#### 5.2 Show the Interface
- **Point out**: Modern ChatGPT-style interface
- **Show**: Dark theme, clean design
- **Highlight**: File upload button (+)

#### 5.3 Configure Settings
1. Click **⚙️ Settings** icon
2. Show that API key is already configured
3. Select model: `llama-3.3-70b-versatile`
4. Close settings

#### 5.4 Upload Test Files
```bash
# Use files from Test_Material folder
# Upload in this order:

1. Click + icon
2. Select: Test_Material/question.pdf (or similar)
3. Upload: Test_Material/rubric.pdf
4. Upload: Test_Material/answer.pdf
```

**Show**: Files appearing in chat

#### 5.5 Request Grading
Type in chat:
```
Please grade this submission using the provided rubric.
```

Press Enter and **show**:
- Loading indicator
- Grading process
- **Final result** with:
  - Score (e.g., 7/10)
  - Detailed breakdown
  - Feedback for each criterion

---

### **STEP 6: Show Docker Features** (On Camera)

#### 6.1 Show Running Container
```bash
# Open new PowerShell window
docker ps
```

**Show output**:
```
CONTAINER ID   IMAGE            STATUS         PORTS                    NAMES
abc123def456   autograde-plus   Up 2 minutes   0.0.0.0:5000->5000/tcp   autograde-plus
```

#### 6.2 Show Container Logs
```bash
docker logs autograde-plus
```

**Show**: All server logs, API calls, grading process

#### 6.3 Show Resource Usage
```bash
docker stats autograde-plus --no-stream
```

**Show**: CPU, Memory usage

---

### **STEP 7: Stop and Clean Up** (On Camera)

```bash
# Stop the container
docker-compose down
```

**Expected Output:**
```
[+] Running 1/1
 ✔ Container autograde-plus  Removed
```

---

## 🎬 Demo Script (What to Say/Show)

### **Scene 1: Introduction** (30 seconds)
```
"This is AutoGrade+, an AI-powered automated grading system.
I'll demonstrate how to run it using Docker for easy deployment."
```

### **Scene 2: Build Image** (1 minute)
```
"First, I'll build the Docker image from the Dockerfile.
This packages the entire application with all dependencies."

[Show: docker build command]
[Show: Build process]
```

### **Scene 3: Run Container** (30 seconds)
```
"Now I'll start the container using docker-compose.
This launches the application in an isolated environment."

[Show: docker-compose up]
[Show: Server starting]
```

### **Scene 4: Demo Application** (2 minutes)
```
"The application is now running on localhost:5000.
Let me show you the interface and grading process."

[Show: Browser opening]
[Show: Modern UI]
[Show: File upload]
[Show: Grading results]
```

### **Scene 5: Docker Management** (1 minute)
```
"Docker makes it easy to manage the application.
I can view running containers, check logs, and monitor resources."

[Show: docker ps]
[Show: docker logs]
[Show: docker stats]
```

### **Scene 6: Conclusion** (30 seconds)
```
"That's AutoGrade+ running in Docker.
It's production-ready and can be deployed anywhere."

[Show: docker-compose down]
```

**Total Time**: ~5 minutes

---

## 📝 Quick Recording Checklist

Before you start recording:

- [ ] Docker Desktop is running (green icon)
- [ ] `.env` file has your API key
- [ ] Test files are ready in `Test_Material/`
- [ ] Browser is closed (will open fresh)
- [ ] Terminal is in project directory
- [ ] Recording software is ready
- [ ] Screen is clean (close unnecessary windows)

---

## 🎥 Recording Tips

### **Video Quality:**
- **Resolution**: 1920x1080 (Full HD)
- **Frame Rate**: 30 FPS
- **Format**: MP4 (most compatible)

### **Audio (Optional):**
- Use built-in mic or headset
- Speak clearly and slowly
- Explain what you're doing

### **Screen:**
- Close unnecessary applications
- Hide personal information
- Use full screen for terminal/browser
- Increase font size for readability

### **Editing (Optional):**
- Speed up build process (2x speed)
- Add text annotations
- Add intro/outro slides

---

## 🚨 Troubleshooting

### **Issue 1: Docker not starting**
```bash
# Restart Docker Desktop
# Or restart computer
```

### **Issue 2: Port 5000 already in use**
```bash
# Stop your current server first
# Or change port in docker-compose.yml:
ports:
  - "5001:5000"  # Use 5001 instead
```

### **Issue 3: Build fails**
```bash
# Check internet connection
# Try again:
docker build -t autograde-plus . --no-cache
```

### **Issue 4: Container won't start**
```bash
# Check logs:
docker logs autograde-plus

# Common fix - check .env file:
notepad .env
```

---

## 📦 Alternative: Quick Demo Without Docker

If Docker gives issues, you can still demo:

```bash
# Method 1: Python directly
python chat_server.py

# Method 2: Batch file
.\start.bat
```

**Then show**:
- "Here's the application running normally"
- "And here's the Dockerfile that would containerize it"
- "This shows the application is Docker-ready"

---

## 🎯 What to Highlight in Video

### **Key Points:**
1. ✅ **Easy Deployment**: One command (`docker-compose up`)
2. ✅ **Isolated Environment**: No system dependencies
3. ✅ **Production Ready**: Can deploy anywhere
4. ✅ **Modern UI**: ChatGPT-style interface
5. ✅ **Accurate Grading**: Shows detailed feedback
6. ✅ **Docker Management**: Easy to monitor and control

---

## 📄 Video Description (For Submission)

```
AutoGrade+ - Docker Deployment Demo

This video demonstrates the AutoGrade+ automated grading system 
running in a Docker container. The system uses:
- ReAct Agent (92% accuracy)
- LoRA Fine-tuned Model (88% accuracy)
- Modern web interface
- Docker containerization for easy deployment

Technologies: Python, Flask, LangChain, Docker, Groq API

GitHub: [your repo]
Paper: AutoGrade+ Research Paper
```

---

## ✅ Final Checklist

After recording:

- [ ] Video shows Docker build process
- [ ] Video shows container running
- [ ] Video shows application working
- [ ] Video shows grading results
- [ ] Video shows Docker management
- [ ] Video is 3-7 minutes long
- [ ] Video is saved as MP4
- [ ] Video quality is good (readable text)

---

**Ready to record?** Follow these steps and you'll have a great demo! 🎬

**Estimated Total Time**: 
- Setup: 5 minutes
- Recording: 5-7 minutes  
- Total: ~12 minutes

Good luck! 🚀
