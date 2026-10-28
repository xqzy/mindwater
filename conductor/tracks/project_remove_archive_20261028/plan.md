# Implementation Plan: Project Removal & Archiving with Cascading Tasks

## Tasks
1. [x] **Database & CRUD Layer (`src/database/crud.py`)**
    - [x] Update `delete_ambition(db, ambition_id)` to delete all tasks linked to `ambition_id` before deleting the ambition.
    - [x] Implement `archive_ambition(db, ambition_id)` to set `ambition.status = "archived"` and set `task.status = "archived"` for all tasks linked to `ambition_id`.
    - [x] Update `get_filtered_tasks(db, role_id, context_tag, energy_level, include_archived=False)` to exclude archived tasks by default.
2. [x] **API Endpoints (`src/api/main.py`)**
    - [x] Update `GET /ambitions` to accept `status: str = "active"`.
    - [x] Add `POST /ambitions/{ambition_id}/archive` endpoint.
    - [x] Update `DELETE /ambitions/{ambition_id}` to validate existence and cascade delete.
    - [x] Update `GET /tasks` to support `include_archived: bool = False`.
3. [x] **Web UI (`src/api/static/index.html`, `src/api/static/app.js`, `src/api/static/style.css`)**
    - [x] Add `#remove-ambition-btn` next to `#edit-ambition-btn` in the Project Details pane (`#ambition-detail`).
    - [x] Add confirmation modal `#project-remove-modal` allowing the user to cancel, archive, or permanently remove the project and its tasks.
    - [x] Add an Active/Archived filter toggle in the Horizons tab and Tasks filter bar so archived items are hidden by default and viewable on demand.
    - [x] Also update the Delete button inside the Edit Ambition modal (`#horizon-delete-btn`) to trigger the same validation flow for consistency.
4. [x] **Verification & Testing (`tests/`)**
    - [x] Add unit and API integration tests in `tests/test_project_remove_archive.py` verifying cascading delete, cascading archive, and default filtering of archived projects/tasks.
    - [x] Run the full test suite (`APP_ENV=test`) to verify zero regressions.
5. [x] **Living Documentation Synchronization**
    - [x] Update `conductor/product.md` with project removal and archiving rules.
    - [x] Mark track complete in `conductor/tracks.md` and `metadata.json`.
