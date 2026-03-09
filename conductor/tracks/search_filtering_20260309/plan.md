# Implementation Plan: Search & Filtering

## Phase 1: Backend Logic Refinement
1. Enhance `src/database/crud.py` to support multi-criteria filtering:
   - Update `filter_tasks` or create a new `get_filtered_tasks` function that handles optional Role, Context, and Energy filters simultaneously.
2. Add a helper function to extract all unique Context tags currently present in the database to populate the filter dropdown.

## Phase 2: Tasks View UI Update
1. Modify `TasksView` in `src/cli/main_tui.py`:
   - Add a `Horizontal` container at the top of the view for the filter widgets.
   - Implement `Select` widgets for Role, Context, and Energy.
   - Add a "Clear" `Button`.

## Phase 3: Dynamic Filtering Logic
1. Implement watchers or event handlers (`on_select_changed`) for the filter widgets.
2. Update `action_refresh_data` to read the current values of all filter widgets and pass them to the backend.
3. Ensure the "Loading" and "Empty" states are handled correctly when filters return no results.

## Phase 4: Integration & UX
1. Populate the filter dropdowns on mount and after significant database changes.
2. Add keyboard shortcuts or focus management to quickly jump to the filter bar.

## Phase 5: Testing & Validation
1. Verify that selecting a filter immediately updates the task list.
2. Verify that multiple filters work in combination (e.g., Work role + @computer context).
3. Ensure "Clear Filters" restores the full list.

## Success Criteria
- [ ] Tasks can be filtered by Context, Energy, and Role.
- [ ] Dropdowns are populated with relevant data.
- [ ] The TUI remains responsive during filtering operations.
