# Todoist Task Push

## Summary
This feature allows users to push their Next Actions from the MindWater TUI directly to their Todoist account.

## Configuration
To use this feature, add your Todoist API token to your credentials JSON file (the same file used for Firebase):

```json
{
  ...
  "todoist_api_token": "your_todoist_api_token_here"
}
```

Alternatively, you can still set it as an environment variable in your `.env` file (as a fallback):

```env
TODOIST_API_TOKEN=your_todoist_api_token_here
```

## Usage
1. Open the **Actions** screen (`ctrl+t`).
2. Select a task in the list.
3. Press **`p`** to push the task to Todoist.
4. A notification will appear at the bottom of the screen indicating success or failure.

## Implementation Details
- **Service**: `src/services/todoist.py`
- **TUI**: `src/cli/main_tui.py` (TasksView)
- **API**: Todoist REST API v2
- **Mapping**: 
    - MindWater Title -> Todoist Content
    - MindWater Planned Date -> Todoist Due Date
