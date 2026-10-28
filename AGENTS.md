# Mindwater — Project Rules & Living Specifications

This repository uses a spec-driven development workflow anchored in the `conductor/` directory. Before planning, modifying, or implementing any code, you MUST respect all core product definitions, technical stack rules, and completed feature specifications.

## 1. Living Product & Technical Specifications

@[Product Definition](conductor/product.md)

@[Product Guidelines](conductor/product-guidelines.md)

@[Tech Stack](conductor/tech-stack.md)

@[Workflow](conductor/workflow.md)

## 2. Historical Feature Registry

All previously implemented features and their detailed specifications live under `conductor/tracks/` and are indexed in:
- @[Tracks Registry](conductor/tracks.md)

When modifying an existing area of the codebase (e.g., Capture, Inbox, Horizons, Weekly Review, Todoist Sync, Email Poller, Web UI, or TUI), inspect the relevant track's `spec.md` in `conductor/tracks/` to ensure backward compatibility and prevent regressions.

## 3. Environment & Database Safety Rules

1. **Never Modify Production Data**:
   - `gtd.db` (and `/app/data/gtd.db`) is the production database.
   - All local development and automated tests MUST run with `APP_ENV=development` (which targets `gtd_dev.db`) or `APP_ENV=test` (`test_gtd.db`) or in-memory SQLite.
2. **Branching & Deployment**:
   - **`dev`**: Active development branch for local coding and testing.
   - **`test`**: Staging/verification branch.
   - **`main`**: Production branch pulled by the Synology NAS Docker container (`http://192.168.1.77:8080`).
3. **Adding New Features**:
   - Whenever the user asks to add a new feature or change functional requirements, activate the `conductor` skill (`.agents/skills/conductor/SKILL.md`) to maintain the living specification and track history.

