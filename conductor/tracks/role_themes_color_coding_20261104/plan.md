# Implementation Plan: Role Color Coding & 15 Cartoon/Disney Card Themes

## Tasks
1. [x] **Database Schema & Auto-Migration (`src/database/models.py`, `src/database/session.py`)**
    - [x] Add `color = Column(String, default="#0284c7")` and `theme_key = Column(String, default="frozen")` to `Horizon2` in `src/database/models.py`.
    - [x] Add `color` and `theme_key` to `h2_role` in `ensure_schema_migrations()` in `src/database/session.py` and populate default themes/colors for existing roles.
2. [x] **CRUD & API Updates (`src/database/crud.py`, `src/api/main.py`)**
    - [x] Update `create_h2`, `update_role`, and `get_ambitions_with_task_counts` in `src/database/crud.py` to support `color` and `theme_key` and pass `role_color` / `role_theme_key` to projects.
    - [x] Update `RoleCreate`, `POST /roles`, and `PUT /roles/{role_id}` in `src/api/main.py`.
3. [x] **15 Cartoon / Disney Themes & Horizons UI (`src/api/static/role_themes.js`, `src/api/static/index.html`, `src/api/static/app.js`, `src/api/static/style.css`)**
    - [x] Create `src/api/static/role_themes.js` with 15 full-bleed SVG cartoon/Disney movie scene illustrations and matching color palettes.
    - [x] Add theme selector grid and color picker to `#role-extra-fields` in `src/api/static/index.html`.
    - [x] Render full-card semi-transparent cartoon banners on Role cards and Role-inherited color coding on Project cards in `src/api/static/app.js` and `src/api/static/style.css`.
4. [x] **Automated Tests (`tests/test_role_themes_colors.py`)**
    - [x] Write unit/integration tests verifying Role creation/updating with `color` and `theme_key`, and verifying `/ambitions` returns `role_color` and `role_theme_key`.
    - [x] Run full test suite (`python -m unittest discover tests -v`).
5. [x] **Living Documentation Synchronization**
    - [x] Update `conductor/product.md`, `conductor/tracks.md`, `plan.md`, and `metadata.json`.
