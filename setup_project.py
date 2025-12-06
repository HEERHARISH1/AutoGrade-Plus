import os
import subprocess
import sys

def create_structure():
    dirs = [
        "data/raw",
        "data/processed",
        "data/rubrics",
        "src/agent",
        "src/finetune",
        "src/evaluation",
        "src/utils",
        "notebooks",
        "paper",
        "prompts"
    ]
    
    base_path = os.getcwd()
    
    for d in dirs:
        path = os.path.join(base_path, d)
        os.makedirs(path, exist_ok=True)
        print(f"Created: {path}")
        
    # Create empty __init__.py files
    for d in ["src", "src/agent", "src/finetune", "src/evaluation", "src/utils"]:
        open(os.path.join(base_path, d, "__init__.py"), 'a').close()

def download_data():
    # Clone the repo containing Mohler dataset
    repo_url = "https://github.com/gsasikiran/Comparative-Evaluation-of-Pretrained-Transfer-Learning-Models-on-ASAG.git"
    target_dir = os.path.join(os.getcwd(), "data", "raw", "mohler_repo")
    
    if not os.path.exists(target_dir):
        print("Cloning Mohler dataset repository...")
        try:
            subprocess.run(["git", "clone", repo_url, target_dir], check=True)
            print("Dataset cloned successfully.")
        except Exception as e:
            print(f"Error cloning dataset: {e}")
    else:
        print("Dataset directory already exists.")

if __name__ == "__main__":
    print("Initializing AutoGrade+ Project...")
    create_structure()
    download_data()
    print("Setup Complete!")
