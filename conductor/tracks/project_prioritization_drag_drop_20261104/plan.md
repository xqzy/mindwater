# Implementation Plan: Project Prioritization & Drag-and-Drop Reordering

## Tasks
1. [x] **Database Schema & Auto-Migration (`src/database/models.py`, `src/database/session.py`)**
    - [x] Add `priority = Column(Integer, default=999)` to `Ambition` in `src/database/models.py`.
    - [x] Add `("priority", "INTEGER DEFAULT 999")` to `ambition` in `ensure_schema_migrations()` in `src/database/session.py` and normalize any uninitialized priorities (`1..N`).
2. [x] **CRUD & Reordering Endpoints (`src/database/crud.py`, `src/api/main.py`)**
    - [x] Update `get_ambitions_with_task_counts`, `get_all_ambitions`, `create_ambition`, and `update_ambition` in `src/database/crud.py` to include `priority`, sort by `(priority, id)`, and re-sequence priorities when a project is inserted or moved to a specific priority number.
    - [x] Add `reorder_ambitions(db, ordered_ids)` in `src/database/crud.py`.
    - [x] Update `AmbitionCreate` and add `POST /ambitions/reorder` in `src/api/main.py`.
3. [x] **Web UI: Priority Input & Drag-and-Drop Cards (`src/api/static/index.html`, `src/api/static/app.js`, `src/api/static/style.css`)**
    - [x] Add `#ambition-priority-input` to `#ambition-extra-fields` in `src/api/static/index.html`.
    - [x] Render priority badge (`#1`, `#2`, ...) with inline quick-edit and HTML5 drag-and-drop handlers (`dragstart`, `dragover`, `dragleave`, `drop`, `dragend`) on `.project-card` in `src/api/static/app.js`.
    - [x] Style `.priority-badge`, `.drag-handle`, `.project-card.dragging`, and `.project-card.drag-over` in `src/api/static/style.css`.
4. [x] **Automated Tests (`tests/test_project_prioritization.py`)**
    - [x] Write unit and integration tests verifying priority number assignment on create/update, automatic re-indexing, and drag-and-drop reordering (`POST /ambitions/reorder`) both globally and within a filtered Role.
    - [x] Run full test suite (`python -m unittest discover tests -v`) to verify zero regressions.
5. [x] **Living Documentation Synchronization**
    - [x] Update `conductor/product.md`, `conductor/tracks.md`, and track `metadata.json`.
