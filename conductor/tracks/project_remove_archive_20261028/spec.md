# Specification: Project Removal & Archiving with Cascading Tasks

## Goal
Provide a button in the "Horizons" tab (inside the Project Details pane, next to the Edit button) that allows the user to remove or archive a Project (Ambition). Require user confirmation first, let the user choose between permanently removing or archiving the project, and cascade that action to all tasks associated with the project.

## Requirements

### 1. Horizons Tab UI (`#ambition-detail`)
- Add a Remove/Archive button (`#remove-ambition-btn`, trash/archive icon) next to the Edit Project button (`#edit-ambition-btn`) in the Project Details pane header.
- Add a toggle/filter in the Horizons Projects section header (`Active Projects` vs `Archived Projects`) and in the Tasks tab filter bar so archived items are hidden from active views by default, with an option to view archived items when desired.

### 2. Confirmation & Action Selection Modal (`#project-remove-modal`)
- Clicking the Remove button opens a dedicated validation modal displaying:
  - The Project (Ambition) title and count of related tasks that will be affected.
  - Clear explanation that all related tasks will also be removed or archived.
  - Three actions for the user:
    - **Cancel**: Close the modal with no changes.
    - **Archive Project & Tasks**: Sets the project status to `"archived"` and sets all associated tasks' status to `"archived"`.
    - **Permanently Delete Project & Tasks**: Permanently deletes the project and all associated tasks from the database.

### 3. Cascading Backend & Database Logic
- **Permanent Removal (`DELETE /ambitions/{ambition_id}`)**:
  - Update `crud.delete_ambition(db, ambition_id)` to first delete all `Task` records where `Task.ambition_id == ambition_id`, and then delete the `Ambition` record in a single transaction.
- **Archiving (`POST /ambitions/{ambition_id}/archive`)**:
  - Add `crud.archive_ambition(db, ambition_id)` which sets `Ambition.status = "archived"` and updates all `Task` records with `Task.ambition_id == ambition_id` to `status = "archived"`.
- **Filtering Active vs. Archived Items**:
  - `GET /ambitions`: Accept an optional `status` query parameter (defaulting to `"active"`).
  - `GET /tasks`: Exclude tasks with `status == "archived"` by default unless `include_archived=true` (or `status="archived"`) is requested.

## Non-Regressions
- Existing project creation, editing, statistics calculation, and role filtering in the Horizons tab must continue to work unchanged.
- Standalone tasks and active project tasks must continue to appear normally in the Tasks tab.
- Weekly Review project listing (`GET /ambitions` default active) must only show active projects.

## Technical Details
- **Database CRUD (`src/database/crud.py`)**:
  - Update `delete_ambition(db, ambition_id)` to cascade-delete tasks.
  - Add `archive_ambition(db, ambition_id)` to cascade-archive tasks.
  - Update `get_filtered_tasks(db, ...)` to filter out `status == "archived"` by default unless `include_archived=True`.
- **API (`src/api/main.py`)**:
  - Update `GET /ambitions` to accept `status: Optional[str] = "active"`.
  - Add `POST /ambitions/{ambition_id}/archive`.
  - Update `DELETE /ambitions/{ambition_id}` to return 404 if not found and cascade delete via CRUD.
  - Update `GET /tasks` to accept `include_archived: bool = False`.
- **Frontend (`src/api/static/index.html`, `src/api/static/app.js`, `src/api/static/style.css`)**:
  - Add `#remove-ambition-btn` in `#ambition-detail`.
  - Add `#project-remove-modal` with Cancel, Archive, and Delete buttons.
  - Add "Show Archived" toggle in Horizons and Tasks views.

