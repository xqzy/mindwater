# Specification: TUI Tasks & Projects View

## Overview
Now that items can be clarified and moved into the local SQLite database, the system needs a way to display and manage these structured tasks. This track will implement a "Tasks" view in the main TUI.

## Requirements

### 1. Interface
- A new "Tasks" tab in the `MindWaterApp`.
- Displays a list (DataTable) of all tasks from the local SQLite `task` table.
- Shows columns: Title, Role, Ambition, Context, Energy, Status.

### 2. Filtering (Contextual View)
- Add quick filters or a way to filter by Context (e.g., @computer) and Energy Level (e.g., Low).
- This aligns with the GTD principle of "Engage" — showing only what can be done right now.

### 3. Management
- Ability to mark a task as "Done" or "Canceled".
- Updating the status in SQLite correctly.

## Success Criteria
- [ ] TUI has a functional "Tasks" tab.
- [ ] Tasks created via the Clarify screen appear in this list.
- [ ] Users can filter the list to focus on specific contexts.
- [ ] Users can update task status (e.g., mark as completed).
