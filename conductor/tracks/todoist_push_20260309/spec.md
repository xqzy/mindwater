# Specification: Todoist Task Push

## Goal
Implement functionality to push next actions (Tasks) from the MindWater Actions screen directly into a user's Todoist account.

## Requirements
1. **Authentication**: Use an API token provided via environment variables (`TODOIST_API_TOKEN`).
2. **Data Preservation**:
    - **Title**: The MindWater task title must become the Todoist task content.
    - **Due Date**: The `planned_date` from MindWater must be preserved as the due date in Todoist.
3. **Trigger**:
    - Add a keyboard binding (e.g., `p`) or a button in the `TasksView` (Actions screen) to push the currently selected task.
4. **Feedback**:
    - Show a success or failure notification in the TUI after the push operation completes.
5. **State Tracking**:
    - (Optional/Phase 2) Mark the task as "Synced" in the local database to avoid duplicate pushes.

## Technical Details
- **API**: Use the Todoist REST API (v2).
- **Library**: `httpx` (already in requirements) for making HTTP requests.
- **Environment**: Ensure `load_dotenv()` is used to pick up the token.
