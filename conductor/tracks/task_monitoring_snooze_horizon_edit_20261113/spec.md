# Specification: Role Theme Picker Fix, Task "Monitoring" Status, Snooze / Due Date, & Horizons Task Editing

## Goal
1. Fix the **Role Theme Picker** in `#horizon-modal` so all 15 cartoon/Disney themes render in a clean, selectable grid without nesting/mixing.
2. Add a **"Monitoring" (`monitoring`)** status for tasks delegated to or waiting on someone else.
3. Provide a **Snooze / Due Date** function (`POST /tasks/{task_id}/snooze` and inside Edit Task) to pick a new due date for any task (including `todo` and `monitoring` tasks).
4. Enable full **Task Editing** (Edit modal, Monitor toggle, Snooze, and Delete) directly from the **Horizons -> Project Details** screen.

## Requirements

### 1. Fix Role Theme Picker Grid (`src/api/static/app.js`, `src/api/static/style.css`)
- Remove the duplicate unclosed `<div>` in `renderRoleThemePicker` and `renderHorizons` so each `.role-theme-option` is an independent selectable card in the 3-column `.role-theme-grid`.

### 2. Task "Monitoring" Status (`src/database/crud.py`, `src/api/main.py`, `src/api/static/app.js`)
- Support `status = "monitoring"` on `Task`.
- In the **Tasks** tab and **Horizons -> Project Details** pane:
  - Display a distinct `<span class="monitoring-badge"><i class="fas fa-eye"></i> Monitoring</span>` badge on tasks with `status == "monitoring"`.
  - Provide a 1-click **Monitor (`fa-eye`)** toggle button on task rows to switch a task between `todo` and `monitoring`, plus a **Status** dropdown (`todo`, `monitoring`, `done`, `archived`) inside the **Edit Task** modal (`#edit-task-status`).
  - Add a status filter (`#filter-status`: `All Active`, `Next Actions (To Do)`, `Monitoring`) in the Tasks filter bar.
- In `get_ambitions_with_task_counts(db, status)`, count both `todo` and `monitoring` tasks as active open steps so projects with monitored tasks are not falsely marked as Stalled (or also return `monitoring_count`).

### 3. Task Snooze / Due Date Function (`src/database/crud.py`, `src/api/main.py`, `src/services/todoist.py`, `src/api/static/index.html`, `src/api/static/app.js`)
- Add `POST /tasks/{task_id}/snooze` accepting `{"due_date": Optional[str]}` (`YYYY-MM-DD` or `null` to clear) and support `due_date` in `PUT /tasks/{task_id}`.
- Updating a task's due date sets `task.todoist_due_date` (`YYYY-MM-DD`) and `task.planned_date` in SQLite, and syncs `due_date` to Todoist if the task is linked to Todoist.
- Add a **Snooze (`fa-clock`)** button on every task row (in both the **Tasks** tab and **Horizons -> Project Details**, for both `todo` and `monitoring` tasks) that opens a **Snooze / Due Date Modal** (`#task-snooze-modal`) with quick presets (`Tomorrow`, `+3 Days`, `Next Week`, `+2 Weeks`, `Clear Date`) and a calendar date input (`#snooze-date-input`).
- Also include a **Due / Snooze Date** input (`#edit-task-due-date`) inside the **Edit Task** modal.

### 4. Edit Tasks from the Horizons Screen (`src/api/static/app.js`)
- In `#detail-tasks` inside the Horizons Project Details pane (`showAmbitionDetail`), add **Edit (`fa-pen-to-square`)**, **Snooze (`fa-clock`)**, and **Monitor (`fa-eye`)** action buttons on every task row.
- Ensure `openTaskEditModal(taskId, ambitionId)` works seamlessly from the Horizons screen and refreshes both the Horizons project cards and `#detail-tasks` upon saving.

## Non-Regressions
- Existing task completion, deletion, role/energy filtering, and Todoist bidirectional sync continue to work without regression.

