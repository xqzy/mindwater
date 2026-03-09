# Specification: TUI Inbox List

## Overview
Create a Terminal User Interface (TUI) to view the items currently in the 'Inbox' collection on Firebase. This will allow users to review what they've captured.

## Requirements

### 1. Interface
- Built with the **Textual** TUI framework.
- A scrollable list showing all items from the `inbox` collection.
- Each item should display:
  - The `clean_text`.
  - Tags and Contexts (if any).
  - The timestamp of capture.

### 2. Data Retrieval
- Fetch documents from the **Firebase Firestore** `inbox` collection.
- Sort by `timestamp` descending (newest first).

### 3. Technical Constraints
- Standalone CLI entry point: `src/cli/tui_inbox.py`.
- Re-use the Firebase initialization from `src/database/firebase.py`.
- Must handle empty inbox states gracefully.

## User Workflow
1. User runs `python -m src.cli.tui_inbox`.
2. A TUI appears with a list of all captured tasks.
3. User can scroll through the list.
4. Pressing 'q' or 'Esc' exits the application.
