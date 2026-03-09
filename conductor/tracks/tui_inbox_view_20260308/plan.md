# Implementation Plan: TUI Inbox Item View & Clarify

## Phase 1: Database Logic
1. Update `src/database/firebase.py` to include a `delete_inbox_item` function.
2. Ensure there's a local database session available to create new Tasks.
3. Verify the existing models (`Role`, `Ambition`, `Task`) in `src/database/models.py`.

## Phase 2: Inbox Item View Screen
1. Modify `src/cli/tui_inbox.py` to handle row selection (Enter).
2. Create a new Screen class `InboxClarifyScreen` in Textual.
3. Layout the view to show `raw_text`, `clean_text`, and the parsed tags/contexts.

## Phase 3: Clarifying Form
1. Add Input widgets for `Task Title`, `Success Outcome`, `Context`, `Energy Level`.
2. Add a way to select existing Roles/Ambitions from the local database.
3. Implement a "Save & Clarify" action.

## Phase 4: Data Integration & Deletion
1. Implement the "Save & Clarify" logic:
   - Create a `Task` object in local SQLite.
   - Link it to the selected Role/Ambition.
   - Delete the item from Firebase Inbox via `delete_inbox_item`.
2. Return to the list view and refresh the inbox list.

## Phase 5: Testing & Validation
1. Manually test the full flow: Capture -> List -> Select -> Clarify -> Verify in SQLite.
2. Ensure connection issues or invalid data are handled gracefully.

## Success Criteria
- [ ] TUI launches the View screen for a selected item.
- [ ] User can input structured GTD data.
- [ ] Item is removed from Firebase and added to SQLite.
- [ ] Local database reflects the new Task correctly.
