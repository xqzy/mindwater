# Implementation Plan: Task Deletion, Completion, and Finalised Tasks Filter

## Tasks
1. [x] **Backend CRUD & API (`src/database/crud.py`, `src/api/main.py`, `src/services/todoist.py`)**
    - [x] Update `crud.get_filtered_tasks` and `GET /tasks` to support `include_completed: bool = False` (hiding `done` tasks by default).
    - [x] Add `crud.delete_task(db, task_id)` and `DELETE /tasks/{task_id}` (including Todoist cleanup if linked).
2. [x] **Web UI: Show Finalised Filter, Mark Done Feedback, & Delete Buttons (`src/api/static/index.html`, `src/api/static/app.js`, `src/api/static/style.css`)**
    - [x] Add `#filter-completed-tasks` ("Show Finalised") checkbox to the Tasks filter bar in `src/api/static/index.html`.
    - [x] Add a Delete button to task rows in `#tasks`, `#detail-tasks`, and `#task-edit-modal`.
    - [x] Style completed task rows (strikethrough + checkmark + Finalised badge) when `Show Finalised` is enabled.
3. [x] **Automated Tests (`tests/test_task_lifecycle.py`)**
    - [x] Write unit and integration tests for hiding/showing finalised (`done`) tasks via `include_completed` and deleting tasks via `DELETE /tasks/{id}`.
    - [x] Run full test suite (`python -m unittest discover tests -v`).
4. [x] **Living Documentation Synchronization**
    - [x] Update `conductor/product.md`, `conductor/tracks.md`, `plan.md`, and `metadata.json`.
