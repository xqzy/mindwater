# Specification: TUI Inbox Item View & Clarify

## Overview
Create a detailed view for a selected item from the Inbox list. This screen will allow users to:
1. Review the raw capture text and parsed data.
2. Decide if it's "Actionable" or not.
3. If actionable, define the:
   - **Next Action** (Title, Context, Energy).
   - **Project** (Success Outcome).
   - **Role/Ambition** it belongs to.
4. If not actionable, delete it or move it to "Someday/Maybe" or "Reference".
5. Upon clarification, the item should be removed from the Firebase 'Inbox' and added to the local SQLite database.

## Requirements

### 1. Interface
- A modal or new screen in the **Textual** TUI.
- Displays all fields of the inbox item (raw_text, clean_text, tags, contexts, timestamp).
- Input fields to modify/add details before saving to the permanent system.

### 2. Integration
- Fetch details of a single item from Firebase.
- Save structured data to the local SQLite database (using `src/database/models.py`).
- Delete the item from Firebase once clarified.

### 3. User Workflow
1. User selects an item in `tui_inbox.py` and presses Enter.
2. The "Inbox View & Clarify" screen appears.
3. User edits the task details.
4. User selects a Role/Ambition (Horizon 2/3) for the task.
5. User presses 's' to "Save/Clarify".
6. The item is saved to SQLite, removed from Firebase, and the user is returned to the Inbox list.

## Success Criteria
- [ ] Able to view full details of an inbox item.
- [ ] User can define Role/Ambition for the item.
- [ ] Clarified items are moved from Firebase to SQLite.
- [ ] User can return to the list view easily.
