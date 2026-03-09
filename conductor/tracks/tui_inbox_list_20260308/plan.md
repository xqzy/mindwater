# Implementation Plan: TUI Inbox List

## Phase 1: Database Logic
1. Update `src/database/firebase.py` to include a `get_inbox_items` function.
2. Ensure it handles connection errors and empty sets.
3. Sort items by `timestamp` descending.

## Phase 2: Core TUI Development
1. Create `src/cli/tui_inbox.py`.
2. Implement a basic **Textual** application structure.
3. Use a `ListView` or `DataTable` widget to display the fetched items.
4. Add basic navigation controls (Scroll, Quit).

## Phase 3: Data Integration
1. Call `get_inbox_items` on app start.
2. Populate the UI with the fetched data.
3. Add a "Refresh" functionality (bound to 'r' key).

## Phase 4: Styling & UI Polish
1. Apply basic styling to the list for readability.
2. Add Header and Footer widgets for context.
3. Ensure long text is handled appropriately (wrapping).

## Phase 5: Testing & Validation
1. Manually test by running `python -m src.cli.tui_inbox`.
2. Verify that it correctly displays items previously captured with `tui_capture`.
3. Check performance with multiple items in the list.

## Success Criteria
- [ ] TUI launches and displays items from Firebase.
- [ ] Items are sorted by newest first.
- [ ] User can scroll through multiple items.
- [ ] Application handles empty state without crashing.
