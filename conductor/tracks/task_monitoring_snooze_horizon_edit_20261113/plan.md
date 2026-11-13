# Implementation Plan: Role Theme Picker Fix, Monitoring Status, Task Snooze, & Horizons Task Editing

## Phase 1: Backend API & Database CRUD
- [x] Update `src/database/crud.py`:
  - Treat `status="monitoring"` alongside `"todo"` as an open task in `get_ambitions_with_task_counts` so projects with delegated/monitored tasks are not flagged as Stalled.
  - Support `status_filter` (`"todo"` / `"monitoring"`) in `get_filtered_tasks`.
  - Support updating `due_date` (`todoist_due_date` and `planned_date`) in `update_task` and add `snooze_task`.
- [x] Update `src/services/todoist.py`:
  - Support clearing or updating `due_date` in `update_todoist_task` and include `monitoring` tasks in two-way completion sync.
- [x] Update `src/api/main.py`:
  - Add `POST /tasks/{task_id}/snooze`.
  - Accept `status_filter` in `GET /tasks` and `due_date` / `status` in `PUT /tasks/{task_id}` and `POST /inbox/{item_id}/clarify`.
  - Include `role_id`, `ambition_id`, `context_tags`, and `due_date` in `GET /ambitions/{ambition_id}/tasks`.

## Phase 2: Frontend UI (`index.html`, `style.css`, `app.js`)
- [x] Fix Role Theme Picker in `src/api/static/app.js` (`renderRoleThemePicker`) and clean up duplicate inner lines in `renderHorizons`.
- [x] Add `monitoring` status option and badge (`fa-eye`), status filter dropdown in `#tasks`, and 1-click monitor toggle button on task rows.
- [x] Add Task Snooze modal (`#task-snooze-modal`) with quick presets (`Tomorrow`, `+3 Days`, `Next Week`, `+2 Weeks`, `Clear Date`) and date picker for both `todo` and `monitoring` tasks.
- [x] Add Edit (`fa-pen-to-square`), Snooze (`fa-clock`), and Monitor (`fa-eye`) buttons to tasks in the Horizons Project Details pane (`#detail-tasks`) and wire `openTaskEditModal` to work from both Tasks and Horizons screens.

## Phase 3: Verification & Living Specification Sync
- [x] Add automated tests in `tests/test_task_lifecycle.py` for `monitoring` status, `POST /tasks/{id}/snooze`, and Horizons task editing.
- [x] Run full test suite inside `mindwater` container (`APP_ENV=test`) and update `conductor/product.md`.
