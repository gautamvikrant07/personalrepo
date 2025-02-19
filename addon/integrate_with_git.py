import os
import subprocess
import streamlit as st
from dotenv import load_dotenv
import requests
import tempfile 
import shutil
from PIL import Image

# Load environment variables
load_dotenv()

GIT_USERNAME = os.getenv("GIT_USERNAME")
GIT_TOKEN = os.getenv("GIT_TOKEN")
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Global variable to store the temporary directory
temp_dir = None

def run_git_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        st.error(f"Git command failed: {e.stderr}")
        raise

def get_github_repos():
    url = f"https://api.github.com/users/{GIT_USERNAME}/repos"
    headers = {
        "Authorization": f"token {GIT_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repos = response.json()
        return [repo['name'] for repo in repos]
    else:
        st.error(f"Failed to fetch repositories: {response.status_code}")
        return []

def clone_repo(repo_name):
    global temp_dir
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp()
    repo_path = os.path.join(temp_dir, repo_name)
    if not os.path.exists(repo_path):
        repo_url = f"https://{GIT_USERNAME}:{GIT_TOKEN}@github.com/{GIT_USERNAME}/{repo_name}.git"
        run_git_command(["git", "clone", repo_url, repo_path])
    return repo_path

def upload_and_commit_code(repo_name, files, commit_message):
    repo_path = clone_repo(repo_name)
    
    # Create a new branch
    branch_name = f"feature/streamlit-upload-{os.urandom(4).hex()}"
    run_git_command(["git", "checkout", "-b", branch_name], cwd=repo_path)

    # Save uploaded files
    for uploaded_file in files:
        file_path = os.path.join(repo_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Stage the file
        run_git_command(["git", "add", uploaded_file.name], cwd=repo_path)

    # Commit changes
    run_git_command(["git", "commit", "-m", commit_message], cwd=repo_path)

    # Push to remote
    run_git_command(["git", "push", "-u", "origin", branch_name], cwd=repo_path)

    return f"Successfully committed and pushed changes to {repo_name} on branch {branch_name}"

def cleanup():
    global temp_dir
    if temp_dir and os.path.exists(temp_dir):
        retry_count = 3
        for _ in range(retry_count):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                break
            except PermissionError:
                time.sleep(1)  # Wait for a second before retrying
        
        # If the directory still exists after retries, silently ignore it
        if os.path.exists(temp_dir):
            pass  # Do nothing, silently ignore the remaining files
        
        temp_dir = None

def git_commit():
    # Load and display the Git logo
    git_logo_path = os.path.join(BASE_PATH, "git_logo.png")
    if os.path.exists(git_logo_path):
        git_logo = Image.open(git_logo_path)
        st.image(git_logo, width=200)  # Adjust width as needed

    st.title("GIT-GPT Integration")

    # Get GitHub repositories
    github_repos = get_github_repos()
    
    # Select GitHub repository
    selected_repo = st.selectbox("Select GitHub Repository", github_repos)
    
    # File uploader
    uploaded_files = st.file_uploader("Upload Code Files", accept_multiple_files=True)
    
    # Commit message
    commit_message = st.text_input("Commit Message", "Auto-commit from CapGenie")
    
    # Commit button
    if st.button("Commit to Git"):
        if selected_repo and uploaded_files:
            with st.spinner("Committing changes..."):
                try:
                    result = upload_and_commit_code(selected_repo, uploaded_files, commit_message)
                    st.success(result)
                finally:
                    # Cleanup temporary files after commit (successful or not)
                    cleanup()
        else:
            st.warning("Please select a repository and upload files before committing.")

# Cleanup when the script is re-run
cleanup()