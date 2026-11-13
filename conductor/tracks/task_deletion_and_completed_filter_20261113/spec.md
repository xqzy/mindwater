# Specification: Task Deletion, Completion, and Finalised Tasks Filter

## Goal
Allow users to:
1. **Mark tasks as Done (Finalised)** so they are hidden from the default active Task List (while still crediting project statistics and syncing completion with Todoist).
2. **Toggle a "Show Finalised" filter** in the Task List (`#tasks`) to choose whether completed (`done`) tasks are visible.
3. **Permanently Delete tasks** when they are no longer needed (from the Task List row actions, the Edit Task modal, and the Horizons Project Details pane).

## Requirements

### 1. Backend CRUD & API (`src/database/crud.py`, `src/api/main.py`, `src/services/todoist.py`)
- **Task Filtering (`GET /tasks` & `crud.get_filtered_tasks`)**:
  - Add `include_completed: bool = False` parameter to `crud.get_filtered_tasks` and `GET /tasks`.
  - When `include_completed=False` (the default), exclude tasks with `status == "done"` so newly finalised tasks disappear from the active Action List.
  - When `include_completed=True`, include tasks with `status == "done"`.
- **Task Deletion (`DELETE /tasks/{task_id}` & `crud.delete_task`)**:
  - Add `crud.delete_task(db, task_id)` to delete a task from SQLite.
  - Add `DELETE /tasks/{task_id}` in `src/api/main.py`. If the task is linked to Todoist (`todoist_task_id`) and a token is configured, attempt to delete/close it in Todoist as well so it isn't re-imported on the next sync.

### 2. Frontend UI (`src/api/static/index.html`, `src/api/static/app.js`, `src/api/static/style.css`)
- **Task List Filter Bar (`#tasks .filter-bar`)**:
  - Add a **Show Finalised** checkbox (`#filter-completed-tasks`) next to **Show Archived** (`#filter-archived-tasks`).
  - Checking/unchecking `#filter-completed-tasks` calls `fetchTasks()` with `include_completed=true`.
- **Marking Tasks Done**:
  - Clicking the status circle (`.status-circle`) on any task row in `#tasks` or `#detail-tasks` toggles its status between `todo` and `done` (`PATCH /tasks/{id}/status`), shows a confirmation toast, and refreshes the list.
  - When `Show Finalised` is checked, completed tasks display a green checkmark circle, strikethrough title, and a `Done` badge.
- **Deleting Tasks**:
  - Add a **Delete** button (`fa-trash-can`) on each task row in the **Tasks** tab (`renderTasks`), in the **Horizons Project Details** task list (`#detail-tasks`), and inside the **Edit Task** modal (`#delete-task-btn`).
  - Clicking Delete asks for confirmation and calls `DELETE /tasks/{task_id}`.

## Non-Regressions
- Completed tasks (`status == "done"`) still count toward Project progress bars and Project time-spent statistics in the Horizons tab.
- Todoist two-way completion sync continues to work seamlessly.

