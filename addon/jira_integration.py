import os
import streamlit as st
from dotenv import load_dotenv
from jira import JIRA
import pandas as pd
from PIL import Image
import requests
import tempfile
import shutil
import subprocess
from openai import OpenAI

# Load environment variables
load_dotenv()

# JIRA credentials
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_INSTANCE_URL = os.getenv("JIRA_INSTANCE_URL")

# Git credentials
GIT_USERNAME = os.getenv("GIT_USERNAME")
GIT_TOKEN = os.getenv("GIT_TOKEN")

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Global variable to store the temporary directory
temp_dir = None

def initialize_jira():
    try:
        jira_client = JIRA(server=JIRA_INSTANCE_URL, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
        return jira_client
    except Exception as e:
        st.error(f"Error connecting to JIRA: {str(e)}")
        return None

def get_projects(jira_client):
    return [{"key": project.key, "name": project.name} for project in jira_client.projects()]

def create_jira_issue(jira_client, project_key, summary, description, issue_type, parent_key=None):
    issue_dict = {
        'project': {'key': project_key},
        'summary': summary,
        'description': description,
        'issuetype': {'name': issue_type},
    }
    if parent_key:
        issue_dict['parent'] = {'key': parent_key}
    print(f"Attempting to create issue with: {issue_dict}")  # Debug print
    try:
        new_issue = jira_client.create_issue(fields=issue_dict)
        return {
            "key": new_issue.key,
            "link": f"{jira_client.server_url}/browse/{new_issue.key}"
        }
    except Exception as e:
        print(f"Error creating JIRA issue: {str(e)}")  # Debug print
        return None

def generate_content(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates content based on user stories."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

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

def run_git_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        st.error(f"Git command failed: {e.stderr}")
        raise

def commit_and_push_changes(repo_path, branch_name, commit_message):
    run_git_command(["git", "add", "."], cwd=repo_path)
    run_git_command(["git", "commit", "-m", commit_message], cwd=repo_path)
    run_git_command(["git", "push", "-u", "origin", branch_name], cwd=repo_path)

def interact_with_jira():
    global temp_dir
    st.title("JIRA and GIT Integration")

    jira_client = initialize_jira()
    if not jira_client:
        return

    # Project selection
    projects = get_projects(jira_client)
    project_options = {f"{p['key']}: {p['name']}": p['key'] for p in projects}
    selected_project = st.selectbox("Select JIRA Project", list(project_options.keys()))
    project_key = project_options[selected_project]

    # Get available issue types for the project
    issue_types = jira_client.project(project_key).issueTypes
    standard_issue_types = [it.name for it in issue_types if not it.subtask]

    # Issue type selection
    selected_issue_type = st.selectbox("Select Issue Type", standard_issue_types)

    # Hardcode subtask type
    subtask_type = "Subtask"

    # Get GitHub repositories
    github_repos = get_github_repos()
    selected_repo = st.selectbox("Select GitHub Repository", github_repos)

    # User story input
    user_story = st.text_area("Enter User Story")

    if st.button("Generate and Create"):
        if user_story and selected_repo:
            with st.spinner("Generating content and creating issues..."):
                # Generate content using AI
                story_prompt = f"Generate a detailed JIRA issue description for the following user story:\n\n{user_story}"
                issue_description = generate_content(story_prompt)

                subtask_prompt = f"Generate a development subtask description for the following user story:\n\n{user_story}"
                subtask_description = generate_content(subtask_prompt)

                code_prompt = f"Generate sample Python code for the following user story:\n\n{user_story}"
                source_code = generate_content(code_prompt)

                test_prompt = f"Generate test cases for the following user story:\n\n{user_story}"
                test_cases = generate_content(test_prompt)

                # Create main JIRA issue
                main_issue = create_jira_issue(jira_client, project_key, user_story, issue_description, selected_issue_type)
                if main_issue:
                    st.success(f"Main issue created: [{main_issue['key']}]({main_issue['link']})")
                    
                    # Create development subtask
                    subtask = create_jira_issue(jira_client, project_key, "Development: " + user_story, subtask_description, subtask_type, main_issue['key'])
                    if subtask:
                        st.success(f"Development subtask created: [{subtask['key']}]({subtask['link']})")
                    else:
                        st.error("Failed to create development subtask")

                    # Commit to GitHub
                    repo_path = clone_repo(selected_repo)
                    branch_name = f"feature/{main_issue['key']}"
                    run_git_command(["git", "checkout", "-b", branch_name], cwd=repo_path)

                    # Save generated files
                    with open(os.path.join(repo_path, f"{main_issue['key']}_implementation.py"), "w") as f:
                        f.write(source_code)
                    with open(os.path.join(repo_path, f"{main_issue['key']}_tests.py"), "w") as f:
                        f.write(test_cases)

                    commit_message = f"Implement {main_issue['key']}: {user_story}"
                    commit_and_push_changes(repo_path, branch_name, commit_message)

                    st.success(f"Changes committed and pushed to {selected_repo} on branch {branch_name}")
                else:
                    st.error("Failed to create main issue")

    # Cleanup
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
        temp_dir = None

if __name__ == "__main__":
    interact_with_jira()