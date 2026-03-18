import os
import httpx
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TODOIST_API_URL = "https://api.todoist.com/rest/v1/tasks"

def get_todoist_token() -> str:
    """Retrieves the Todoist token from the credentials JSON file."""
    # First, try to get it from the JSON file referenced in FIREBASE_CREDENTIALS
    cred_path = os.environ.get("FIREBASE_CREDENTIALS")
    
    # If not in env, search for mindwater-*.json in root
    if not cred_path:
        import glob
        matches = glob.glob("mindwater-*.json")
        if matches:
            cred_path = matches[0]

    if cred_path and os.path.exists(cred_path):
        try:
            with open(cred_path, 'r') as f:
                creds = json.load(f)
                token = creds.get("todoist_api_token")
                if token:
                    return token
        except Exception:
            pass
    
    # Fallback to environment variable if JSON retrieval fails
    return os.environ.get("TODOIST_API_TOKEN")

def push_task_to_todoist(title: str, due_date: datetime = None) -> str:
    """
    Pushes a task to Todoist.
    
    Args:
        title: The task title (content in Todoist).
        due_date: Optional due date.
        
    Returns:
        The ID of the created task.
        
    Raises:
        ValueError: If API token is missing.
        RuntimeError: If the API request fails.
    """
    token = get_todoist_token()
    if not token:
        raise ValueError("Todoist API token not found in credentials file or environment variables.")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = {
        "content": title,
    }

    if due_date:
        # Todoist expects YYYY-MM-DD or RFC3339
        if isinstance(due_date, datetime):
            data["due_date"] = due_date.strftime("%Y-%m-%d")
        elif isinstance(due_date, str):
            data["due_date"] = due_date

    try:
        with httpx.Client() as client:
            response = client.post(TODOIST_API_URL, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result.get("id")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Todoist API error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        raise RuntimeError(f"Failed to push to Todoist: {str(e)}")
