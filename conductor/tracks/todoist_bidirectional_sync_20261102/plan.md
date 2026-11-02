# Implementation Plan: Bi-Directional Todoist Integration & Mapping

## Tasks
1. [x] **Database Models & Safe Auto-Migration (`src/database/models.py`, `src/database/session.py`, `src/database/crud.py`)**
    - [x] Add `AppSetting` model (`key`, `value`, `updated_at`) for storing `todoist_api_token` and sync metadata in SQLite.
    - [x] Add Todoist fields to existing models:
        - `Horizon2`: `todoist_project_id`, `todoist_project_name`
        - `Ambition`: `todoist_label_id`, `todoist_label_name`
        - `Task`: `todoist_task_id`, `todoist_due_date`, `todoist_priority`, `todoist_created_at`
        - `Inbox`: `todoist_task_id`, `todoist_due_date`, `todoist_priority`, `todoist_created_at`
    - [x] Add idempotent column migration in `init_db()` (`src/database/session.py`) so existing databases (`gtd_dev.db` and `gtd.db`) gain the new columns and `app_setting` table automatically on startup.
2. [x] **Todoist Unified API v1 Service & Sync Engine (`src/services/todoist.py`)**
    - [x] Upgrade endpoints to `https://api.todoist.com/api/v1` (with pagination envelope support).
    - [x] Read/save token via `AppSetting` table (with fallback to `TODOIST_API_TOKEN` env var).
    - [x] Implement Todoist API client functions for Projects, Labels, and Tasks (create, update, close, reopen, delete, list active, sync duration/due/priority).
    - [x] Implement `sync_with_todoist(db)` orchestrator:
        - Fetch remote Todoist projects, labels, and active tasks.
        - Route mapped tasks to `Task` and unmapped tasks to `Inbox`.
        - Mark local `todo` tasks with `todoist_task_id` as `done` if completed in Todoist.
3. [x] **Backend API Endpoints (`src/api/main.py`)**
    - [x] `GET /todoist/settings` & `POST /todoist/settings` (sticky token management & status).
    - [x] `GET /todoist/mappings` & `POST /todoist/mappings/role` & `POST /todoist/mappings/ambition` (mapping table CRUD + 1-click remote creation).
    - [x] `POST /todoist/sync` (manual and on-tab-open bi-directional sync).
    - [x] `POST /tasks/batch-push-todoist` (batch push for Weekly Review Step 2).
    - [x] Hook Todoist updates into `PATCH /tasks/{id}/status`, `PUT /tasks/{id}`, `POST /inbox/{id}/clarify`, `PUT /roles/{id}`, `PUT /ambitions/{id}`, `POST /ambitions/{id}/archive`, and `DELETE /ambitions/{id}`.
4. [x] **Web UI (`src/api/static/index.html`, `src/api/static/app.js`, `src/api/static/style.css`)**
    - [x] Add a **Todoist** navigation tab containing:
        - Sticky API Token configuration bar (masked token indicator + Save + Sync Now button).
        - Role (H2) $\leftrightarrow$ Todoist Project mapping table.
        - Mindwater Project (H1) $\leftrightarrow$ Todoist Label mapping table.
    - [x] Add **Sync with Todoist** button and automatic sync on tab open (`inbox`, `tasks`, `todoist`), plus Urgent/Due and Synced Deep-Link badges in Inbox, Tasks, and Horizons.
    - [x] Enhance Weekly Review Step 2 with task checkboxes + **"Push Selected to Todoist"** button and the **"Stale in Todoist (>14 days)"** check.
5. [x] **Automated Verification (`tests/test_todoist_sync.py`)**
    - [x] Write unit and integration tests mocking Todoist REST v2 responses to verify token persistence, mapping table, inbox/task routing, clarify-in-place, 2-way completion sync, duration sync, batch push, and stale task detection.
    - [x] Run full test suite (`python -m unittest discover tests -v`) to verify zero regressions.
6. [x] **Living Documentation Synchronization**
    - [x] Update `conductor/product.md` and `conductor/tracks.md`.
