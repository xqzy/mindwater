# Implementation Plan: TUI Inbox Delete

## Phase 1: Track Setup
- [x] Create the track directory and files.

## Phase 2: Extend TUI Metadata
1. Modify `TUIInboxApp` in `src/cli/tui_inbox.py` to store document IDs.
   - When populating the `DataTable`, include the `id` of each Firebase item, possibly in a hidden way or simply associated with the row key.

## Phase 3: Add Binding and Action
1. Add `("d", "delete_selected", "Delete Item")` to the `BINDINGS` list in `TUIInboxApp`.
2. Implement `action_delete_selected` in `src/cli/tui_inbox.py`.
   - Identify the selected row.
   - Retrieve the associated document ID.
   - Call `delete_inbox_item(doc_id)` from `src/database/firebase.py`.
   - Update the UI: either remove the row from the `DataTable` or trigger a refresh.

## Phase 4: UI Refinement and Feedback
1. (Optional) Implement a simple confirmation prompt before deletion.
2. Ensure status messages are correctly updated or displayed on success/failure.

## Phase 5: Testing
1. Manually test the delete functionality.
2. Verify that deleting an item successfully removes it from the Firebase `inbox` collection.
3. Verify that the UI reflects the change immediately.

## Success Criteria
- [ ] Pressing 'd' on a selected inbox item deletes it from Firebase.
- [ ] The TUI UI updates correctly after deletion.
- [ ] Error handling is implemented for failed deletions.
