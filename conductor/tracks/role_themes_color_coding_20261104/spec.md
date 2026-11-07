# Specification: Role Color Coding & 15 Cartoon/Disney Card Themes

## Goal
Allow users to style **Roles (`Horizon2`)** with custom color coding and choose from **15 cartoon / Disney movie banner illustrations** that span across the entire Role card semi-transparently behind the text, with colors matching the chosen picture. All **Projects (`Ambition`)** automatically follow the color coding of their assigned Role.

## Requirements

### 1. Data Model & Auto-Migration (`Horizon2`)
- Add two columns to `Horizon2` (`h2_role` table) in `src/database/models.py`:
  - `color = Column(String, default="#4f46e5")` (Hex color code for the Role)
  - `theme_key = Column(String, nullable=True)` (Identifier for one of the 15 cartoon/Disney illustrations)
- Update `ensure_schema_migrations()` in `src/database/session.py` to safely add `color` and `theme_key` to `h2_role` on existing SQLite databases (`gtd_dev.db` and `gtd.db`), and assign default matching themes/colors to existing roles if unset.

### 2. API & CRUD Support (`src/database/crud.py`, `src/api/main.py`)
- Update `RoleCreate` in `src/api/main.py` to accept `color: Optional[str] = "#4f46e5"` and `theme_key: Optional[str] = None`.
- Update `create_role` and `update_role` in `src/database/crud.py` to persist `color` and `theme_key`.
- Update `get_ambitions_with_task_counts` in `src/database/crud.py` to include `role_color` and `role_theme_key` in each returned project object so Projects automatically inherit their Role's color coding.

### 3. 15 Cartoon / Disney Movie Themes & Matching Color Palettes (`src/api/static/role_themes.js`)
Provide 15 selectable cartoon/Disney movie panoramic card illustrations, each with a matching primary color and soft surface tint:
1. `lion_king` — **The Lion King (Pride Rock Sunrise)** — Savanna Amber (`#d97706`)
2. `frozen` — **Frozen (Arendelle Ice Palace)** — Glacial Cyan (`#0284c7`)
3. `aladdin` — **Aladdin (Arabian Nights & Magic Carpet)** — Royal Genie Violet (`#7c3aed`)
4. `moana` — **Moana (Motunui Ocean Voyage)** — Pacific Lagoon Teal (`#0d9488`)
5. `toy_story` — **Toy Story (Cloud Sky & Sheriff Star)** — Sky Ranger Blue (`#2563eb`)
6. `beauty_beast` — **Beauty and the Beast (Enchanted Rose)** — Enchanted Crimson (`#e11d48`)
7. `little_mermaid` — **The Little Mermaid (Atlantica Reef)** — Seafoam Emerald (`#059669`)
8. `tangled` — **Tangled (Floating Lanterns of Corona)** — Lantern Magenta (`#c026d3`)
9. `up` — **Up (Paradise Falls Balloon House)** — Adventure Sunset Orange (`#ea580c`)
10. `finding_nemo` — **Finding Nemo (Great Barrier Reef)** — Clownfish Coral (`#f97316`)
11. `mulan` — **Mulan (Cherry Blossom Imperial Garden)** — Blossom Rose (`#db2777`)
12. `wall_e` — **WALL-E (Starlight & Plant Sprout)** — Sprout Lime (`#65a30d`)
13. `coco` — **Coco (Marigold Bridge Fiesta)** — Marigold Gold (`#ca8a04`)
14. `monsters_inc` — **Monsters, Inc. (Monstropolis Doors)** — Sulley Aqua (`#0891b2`)
15. `peter_pan` — **Peter Pan (Neverland Second Star)** — Pixie Forest Green (`#16a34a`)

### 4. Role Card & Project Card Visual Styling (`src/api/static/index.html`, `src/api/static/app.js`, `src/api/static/style.css`)
- **Role Cards**:
  - The selected cartoon/Disney illustration spans across the entire Role card (`position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;`) with semi-transparency so the foreground elements remain crisp and readable.
  - Each Role card displays a small, recognizable, **full-color pictogram** (`iconSvg`) of the related cartoon/Disney movie inside a dedicated 38×38px badge (`role-movie-pictogram`, `flex-shrink: 0`) in its own left column so that text (`role-card-text`) and action buttons (`fa-gear`) never overlap or mingle with the pictogram.
  - The selected cartoon/Disney illustration spans across the entire Role card (`position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.78;`) with a light left-to-right veil so the colors and artwork are rich and clearly visible while keeping the Role name, Todoist mapping subtitle, and settings button crisp in front.
  - Card border, accent bar, and active state match the Role's color.
- **Project Cards**:
  - Inherit their Role's color coding: colored left border accent, subtle tinted card surface, Role badge in the Role's color, priority badge (`#1`, `#2`) accented in the Role's color, and progress bar filled with the Role's color.
- **Role Add/Edit Modal (`#horizon-modal`)**:
  - Displays a 15-card visual theme selector grid and a color picker (`#role-color-input`). Selecting a cartoon/Disney picture automatically sets the matching color (which can also be fine-tuned).

## Non-Regressions
- Project drag-and-drop reordering and inline priority editing continue to work seamlessly.
- Role filtering, Todoist project/label mappings, and Weekly Review continue to function without regression.

