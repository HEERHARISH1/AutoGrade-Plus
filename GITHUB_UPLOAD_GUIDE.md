# 🚀 GitHub Upload Guide for AutoGrade+

## Quick Steps to Upload Your Project to GitHub

### Option 1: Using GitHub Desktop (Easiest)

1. **Download GitHub Desktop**
   - Go to: https://desktop.github.com/
   - Install and sign in with your GitHub account

2. **Create New Repository**
   - Click "File" → "New Repository"
   - Name: `AutoGrade-Plus`
   - Description: "AI-Powered Automated Grading System - ReAct vs LoRA"
   - Choose this folder as location
   - Click "Create Repository"

3. **Publish to GitHub**
   - Click "Publish repository"
   - Uncheck "Keep this code private" (or keep it private)
   - Click "Publish repository"

4. **Done!** Your code is now on GitHub
   - Copy the repository URL
   - Update `SUBMISSION_README.md` with your GitHub link

---

### Option 2: Using Git Command Line

1. **Install Git**
   ```powershell
   winget install Git.Git
   ```

2. **Initialize Repository**
   ```bash
   cd "c:\Users\heerh\OneDrive\Desktop\FAST\7th_Semester\GenAI\Project_i222371"
   git init
   git add .
   git commit -m "Initial commit: AutoGrade+ complete implementation"
   ```

3. **Create Repository on GitHub**
   - Go to: https://github.com/new
   - Name: `AutoGrade-Plus`
   - Description: "AI-Powered Automated Grading System"
   - Don't initialize with README (we already have one)
   - Click "Create repository"

4. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/AutoGrade-Plus.git
   git branch -M main
   git push -u origin main
   ```

---

### Option 3: Upload via GitHub Web Interface

1. **Create New Repository**
   - Go to: https://github.com/new
   - Name: `AutoGrade-Plus`
   - Click "Create repository"

2. **Upload Files**
   - Click "uploading an existing file"
   - Drag and drop your project folder
   - Commit changes

**Note:** This method has file size limits. Use Option 1 or 2 for large projects.

---

## 📝 What to Include in GitHub Repository

### ✅ Include These Files:
- All `.py` files
- `requirements.txt`
- `Dockerfile` and `docker-compose.yml`
- `frontend/` folder (HTML, CSS, JS)
- `src/` folder (all source code)
- `prompts/` folder
- `README.md`
- `QUICK_START.md`
- `training_data.jsonl`
- Test materials

### ❌ Exclude These Files:
- `__pycache__/` folders
- `.env` file (contains API keys!)
- `lora_model/` (too large - mention in README how to download)
- `*.pyc` files
- Large PDF files in `paper/`
- Debug logs

---

## 🔒 Create .gitignore File

Create a file named `.gitignore` in your project root:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Environment
.env
.venv
env/
venv/

# Models (too large)
lora_model/
*.bin
*.safetensors

# Logs
*.log
debug_log.txt
extraction_log.txt

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Large files
*.pdf
*.zip
```

---

## 📋 After Uploading to GitHub

1. **Get Your Repository URL**
   - Example: `https://github.com/YOUR-USERNAME/AutoGrade-Plus`

2. **Update SUBMISSION_README.md**
   - Replace `[YOUR-USERNAME]` with your actual GitHub username
   - Replace `[Your Email]` with your email
   - Replace `[Your GitHub Profile]` with your profile URL

3. **Test the Repository**
   - Try cloning it: `git clone YOUR-REPO-URL`
   - Verify all files are there
   - Check README displays correctly

4. **Make Repository Public** (if required)
   - Go to repository Settings
   - Scroll to "Danger Zone"
   - Click "Change visibility" → "Make public"

---

## 🎯 Final Submission Package

After uploading to GitHub, create a ZIP file with:

```
i222371_Heer_GenAI_Project.ZIP
├── SUBMISSION_README.md        (with GitHub link)
├── SUBMISSION_PROMPTS_LOG.txt  (all prompts)
├── Final_project_Report.pdf    (from paper/ folder)
└── i222371_GenAI_Project_Proposal.pdf
```

---

## 🚀 Quick Commands Cheat Sheet

```bash
# Check Git status
git status

# Add all files
git add .

# Commit changes
git commit -m "Your message"

# Push to GitHub
git push

# Pull latest changes
git pull

# View repository URL
git remote -v
```

---

## ❓ Troubleshooting

### Problem: "Git not found"
**Solution:** Install Git first
```powershell
winget install Git.Git
```

### Problem: "Permission denied"
**Solution:** Set up SSH key or use GitHub Desktop

### Problem: "File too large"
**Solution:** Add to `.gitignore` and use Git LFS
```bash
git lfs install
git lfs track "*.bin"
```

### Problem: "Repository already exists"
**Solution:** Use a different name or delete the old repository

---

## 📞 Need Help?

- GitHub Docs: https://docs.github.com
- GitHub Desktop Guide: https://docs.github.com/en/desktop
- Git Tutorial: https://git-scm.com/docs/gittutorial

---

**Recommended:** Use GitHub Desktop (Option 1) - it's the easiest and most reliable method!

Good luck with your submission! 🎉
