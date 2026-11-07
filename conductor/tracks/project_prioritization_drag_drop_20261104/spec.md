# Specification: Project Prioritization & Drag-and-Drop Reordering

## Goal
Enable users to prioritize Projects (`Ambition`) in the **Horizons** tab in two complementary ways:
1. By entering or editing an explicit **Priority Number** (e.g., `#1`, `#2`, `#3`...) in the Add/Edit Project modal or directly on the project card.
2. By **dragging and dropping** project cards into different positions within the Horizons project grid.

## Requirements

### 1. Data Model & Auto-Migration (`Ambition.priority`)
- Add an integer `priority` field to `Ambition` (`src/database/models.py`), defaulting to sequential 1-based ordering (`1, 2, 3, ...`) where lower numbers represent higher priority (`#1` is highest priority).
- Update `ensure_schema_migrations()` in `src/database/session.py` to safely add `priority INTEGER` to the `ambition` table on existing SQLite databases (`gtd_dev.db` and `gtd.db`), and initialize any `NULL` or `0` priorities on active projects to sequential numbers (`1..N`) ordered by `id`.

### 2. Priority Ordering & Reindexing Logic (`src/database/crud.py`, `src/api/main.py`)
- **Default Sort Order**:
  - `get_ambitions_with_task_counts(db, status)` and `get_all_ambitions(db)` return projects ordered by `(Ambition.priority.asc(), Ambition.id.asc())`.
- **Creating a Project (`POST /ambitions`)**:
  - Accepts an optional `priority: Optional[int]` in `AmbitionCreate`.
  - If `priority` is provided, insert the project at that priority position and shift subsequent active projects down (`+1`) so priorities remain clean and sequential (`1..N`).
  - If `priority` is omitted, assign `max(priority) + 1` (placing it at the end of the list).
- **Editing a Project (`PUT /ambitions/{ambition_id}`)**:
  - Accepts `priority: Optional[int]` in `AmbitionCreate`.
  - When a user changes a project's priority number (either via the Edit Project modal or inline on the card), move the project to that target priority slot and re-normalize the priorities of all active projects (`1..N`) so there are no duplicate or skipped numbers.
- **Drag-and-Drop Reordering (`POST /ambitions/reorder`)**:
  - Accepts `{ "ordered_ids": List[int] }` representing the new order of visible project cards.
  - Works seamlessly both when viewing **All Projects** and when filtering by a specific **Role**:
    - Takes the priority slots previously occupied by those `ordered_ids` (sorted ascending) and assigns them in the new `ordered_ids` sequence, then normalizes active project priorities (`1..N`).

### 3. Horizons UI (`src/api/static/index.html`, `src/api/static/app.js`, `src/api/static/style.css`)
- **Project Cards (`#ambitions-list`)**:
  - Each project card displays:
    - A visual drag handle (`fa-grip-vertical`) and `draggable="true"`.
    - An interactive **Priority Badge** (`#1`, `#2`, etc.) on the card. Clicking the priority badge (or typing a number in the inline input) lets the user set the priority number directly, or they can set it in the **Add/Edit Project Modal** (`#horizon-modal`).
  - Dragging a project card and dropping it onto another project card immediately reorders the cards in the UI and persists the new priority order via `POST /ambitions/reorder`.
- **Add/Edit Project Modal (`#horizon-modal`)**:
  - Include a **Priority (1 = Highest)** number input field (`#ambition-priority-input`) inside `#ambition-extra-fields`.

## Non-Regressions
- Clicking a project card still opens `#ambition-detail` with project statistics, Next Actions, Edit, and Remove/Archive buttons.
- Archiving or deleting a project still cascades to tasks and keeps active project priorities clean.
- Todoist Label mappings and Weekly Review project lists automatically benefit from the new priority order.

