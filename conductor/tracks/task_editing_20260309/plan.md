# Plan: Task Details Editing

## Phase 1: Data Schema
- [x] Add `planned_date` and `estimated_time` to `src/database/models.py`.
- [x] Add `planned_date` to `src/models/gtd.py`.

## Phase 2: CRUD Operations
- [x] Update `create_task` in `src/database/crud.py` to support new fields.
- [x] Add `update_task` function in `src/database/crud.py`.

## Phase 3: TUI Implementation
- [x] Create `TaskEditScreen` class in `src/cli/main_tui.py`.
- [x] Implement field population from existing task data.
- [x] Implement save logic with `update_task`.
- [x] Add 'e' key binding to `TasksView`.
- [x] Update `TasksView` to handle the edit action and refresh data.

## Phase 4: Verification
- [x] Run database CRUD tests.
- [x] Run model tests.
- [x] Verify TUI compilation.
