import os
import requests
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# JIRA credentials
jira_instance_url = os.getenv('JIRA_INSTANCE_URL')
jira_email = os.getenv('JIRA_EMAIL')
jira_api_token = os.getenv('JIRA_API_TOKEN')

# Set up headers
auth = base64.b64encode(f"{jira_email}:{jira_api_token}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth}",
    "Accept": "application/json"
}

# Try different endpoints
endpoints = [
    "/rest/api/2/myself",
    "/rest/api/2/serverInfo",
    "/rest/api/2/permissions"
]

for endpoint in endpoints:
    url = f"{jira_instance_url}{endpoint}"
    print(f"\nAttempting to connect to: {url}")
    print(f"Using email: {jira_email}")
    print(f"Token (first 5 chars): {jira_api_token[:5]}...")

    try:
        response = requests.get(url, headers=headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response text: {response.text[:200]}...")  # Print first 200 characters
        
        response.raise_for_status()
        print("Successfully authenticated and received data")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Test connection without authentication
print("\nTesting connection without authentication:")
try:
    response = requests.get(f"{jira_instance_url}/status")
    print(f"Status response code: {response.status_code}")
    print(f"Status response text: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error connecting without auth: {e}")
