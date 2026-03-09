# Implementation Plan: TUI Tasks & Projects View

## Phase 1: CRUD & Backend Logic
1. Update `src/database/crud.py` to include:
   - `get_all_tasks(db)`
   - `update_task_status(db, task_id, status)`
2. Ensure relationships in `src/database/models.py` allow easy access to Role/Ambition names from a Task object.

## Phase 2: Core Tasks TUI Component
1. Create `TasksView(Static)` component in `src/cli/main_tui.py`.
2. Use a `DataTable` to display tasks.
3. Implement `action_refresh_data` (threaded) similar to `InboxListView`.

## Phase 3: Filtering & Integration
1. Add a simple filtering UI (e.g., a `Select` or `Input`) or global keybinds for filtering.
2. Integrate the new view as a third tab in `MindWaterApp`.

## Phase 4: Status Management
1. Add a way to mark tasks as "Done" (e.g., press 'd' on a row).
2. Ensure the SQLite database is updated and the view refreshes.

## Phase 5: Testing & Final Polish
1. Verify the full lifecycle: Capture -> Clarify -> Tasks View -> Mark Done.
2. Ensure consistent styling and layout.

## Success Criteria
- [ ] Users can see their structured tasks.
- [ ] Role and Ambition names are visible in the list.
- [ ] Tasks can be completed within the TUI.
