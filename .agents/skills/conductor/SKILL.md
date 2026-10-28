---
name: conductor
description: >-
  Spec-driven development workflow for Mindwater. Activate this skill whenever the user asks to design, plan, or implement a new feature, change functional requirements, or start a new development track. Ensures new functionality is documented in `conductor/tracks/`, checked against past specifications, tested safely in `dev`, and synchronized with `conductor/product.md`.
---

# Conductor: Spec-Driven Feature Development

Mindwater maintains a cumulative history of functional specifications in the `conductor/` directory so that every feature builds sustainably on top of previous requirements.

Follow these steps whenever adding or updating functionality:

## Step 1: Review Existing Specifications
1. Read `conductor/product.md` and `conductor/tracks.md` (already linked in `AGENTS.md`).
2. Identify any previous tracks in `conductor/tracks/<track_id>/spec.md` that touch the same domain (e.g., Capture, Clarify, Horizons, Tasks, Weekly Review, Todoist, Email, Web UI, or TUI).
3. Read those `spec.md` files to ensure your design preserves existing requirements and constraints.

## Step 2: Create a New Feature Track
Create a new directory `conductor/tracks/<short_snake_case_name>_<YYYYMMDD>/` containing three files:

1. **`metadata.json`**:
   ```json
   {
     "track_id": "<short_snake_case_name>_<YYYYMMDD>",
     "type": "feature",
     "status": "in_progress",
     "created_at": "<ISO-8601-timestamp>",
     "updated_at": "<ISO-8601-timestamp>",
     "description": "<One-sentence summary of the feature>"
   }
   ```
2. **`spec.md`**:
   - **Goal**: Clear statement of what the feature achieves.
   - **Requirements**: Numbered functional requirements, edge cases, and UX/UI behavior.
   - **Non-Regressions**: Existing behaviors that must remain intact.
   - **Technical Details**: Database models, API endpoints, Frontend/TUI components affected.
3. **`plan.md`**:
   - Checklist (`- [ ]`) of implementation tasks broken down into Database/Backend, UI (Web/TUI), Verification (Automated Tests), and Documentation.

Append the new track entry to `conductor/tracks.md`. Pause and confirm the spec/plan with the user if any requirements are ambiguous.

## Step 3: Implement & Verify Safely
1. Ensure you are working on the `dev` branch (unless instructed otherwise).
2. Run all tests with `APP_ENV=test` or `APP_ENV=development` (never against production `gtd.db`).
3. Write unit/integration tests in `tests/` covering the new `spec.md` requirements.
4. Run the full test suite (`python3 -m unittest discover tests`) to verify zero regressions across all historical tracks.
5. Check off completed items (`- [x]`) in the track's `plan.md` as you progress.

## Step 4: Synchronize Living Documentation (Mandatory)
Once implementation and tests pass, you MUST update the living specifications (which are dynamically embedded into `AGENTS.md`):
1. **Update `conductor/product.md`**: Always add or update the relevant section in `conductor/product.md` with the new functional behavior, business rules, or constraints introduced by the feature.
2. **Update `conductor/tech-stack.md`**: Update if any new libraries, endpoints, or architectural patterns were added.
3. **Update `conductor/tracks.md`**: Mark the track as `[x]` in `conductor/tracks.md`.
4. **Update `metadata.json`**: Set `"status": "completed"` and update `"updated_at"` in the track's `metadata.json`.

