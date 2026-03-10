# Implementation Plan: TUI Horizon Refinement

## Phase 1: Database Logic (CRUD & Stats)
1. Add statistics helper functions in `src/database/crud.py`:
   - `get_ambition_stats(db, ambition_id)`: To calculate hours spent, and task counts for the last 6 and 2 weeks.
2. Ensure `get_ambitions_by_role(db, role_id)` is available or updated.

## Phase 2: HorizonsView Filtering Logic
1. Update `HorizonsView.on_data_table_row_selected` to handle role selection.
2. Implement `load_ambitions_by_role(role_id)` to filter the ambitions table.
3. Update `load_ambition_tasks(ambition_id)` to also trigger the statistics update.

## Phase 3: Editing Support (Modal Screens)
1. Create `EditRoleScreen(ModalScreen)` in `src/cli/main_tui.py` for updating name and description.
2. Create `EditAmbitionScreen(ModalScreen)` for updating outcome and status.
3. Add `BINDINGS = [("e", "edit_selected", "Edit")]` to `HorizonsView`.
4. Implement `action_edit_selected` to push the correct edit screen based on focused table.

## Phase 4: Statistics Display
1. Create an `AmbitionStats(Static)` component in `src/cli/main_tui.py`.
2. Integrate it into `HorizonsView.compose` (perhaps next to the tasks table).
3. Implement a method to update the stats view when an ambition is selected.

## Phase 5: UI/UX Refinement & Testing
1. Ensure the hierarchy behaves intuitively (clearing filters, etc.).
2. Add error handling for database updates.
3. Manually verify all filtering, editing, and statistics calculations.

## Success Criteria
- [ ] Selecting a Role filters the Ambitions table.
- [ ] Selecting an Ambition filters the Tasks table.
- [ ] Selecting an Ambition displays correct statistics (hours, recent throughput).
- [ ] Pressing 'e' opens the correct edit dialog for Role/Ambition.
- [ ] Edited values are saved and immediately reflected in the TUI.
