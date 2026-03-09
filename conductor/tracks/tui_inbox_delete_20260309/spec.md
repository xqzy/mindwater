# Specification: TUI Inbox Delete

## Overview
Enhance the existing TUI Inbox view (`src/cli/tui_inbox.py`) by adding the ability to delete a selected task directly from the interface using a keyboard shortcut.

## Requirements

### 1. User Interface
- A new keyboard binding for 'd' that triggers the deletion of the currently selected row in the `DataTable`.
- A confirmation dialog or some form of visual feedback (optional but recommended) to prevent accidental deletions.

### 2. Data Deletion
- When 'd' is pressed, the application should retrieve the document ID of the selected item.
- Call the `delete_inbox_item(doc_id)` function from `src/database/firebase.py`.
- Upon successful deletion, the row should be removed from the TUI `DataTable` without requiring a full manual refresh.

### 3. Error Handling
- Display an error message if the deletion fails (e.g., due to network issues).

## User Workflow
1. User runs `python -m src.cli.tui_inbox`.
2. User navigates to a specific task in the list using arrow keys.
3. User presses the 'd' key.
4. The task is deleted from Firebase.
5. The TUI list updates to reflect that the task is gone.
