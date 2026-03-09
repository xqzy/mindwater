# Implementation Plan: Project Management

## Phase 1: CRUD Expansion
1. Update `src/database/crud.py` to include more robust update and delete functions for Roles and Ambitions if necessary. (Already have basic create/get).

## Phase 2: Creation Dialogs
1. Implement `AddRoleScreen(Screen)` with inputs for Name and Description.
2. Implement `AddAmbitionScreen(Screen)` with inputs for Outcome and a `Select` for Role.

## Phase 3: Horizons View Component
1. Create `HorizonsView(Static)` component.
2. Implement a two-column or stacked layout:
    - **Top/Left:** Roles DataTable.
    - **Bottom/Right:** Ambitions DataTable (grouped by Role).
3. Add "Add Role" and "Add Ambition" buttons with global keybindings (e.g., `Shift+R`, `Shift+A`) when this tab is active.

## Phase 4: Integration
1. Add the "Horizons" tab to `MindWaterApp`.
2. Add navigation bindings (`Ctrl+H` for Horizons).
3. Ensure the `InboxClarifyScreen` re-runs `load_db_options` whenever it is mounted to pick up new Roles/Ambitions.

## Phase 5: Testing & UI Polish
1. Test creating a Role, then creating an Ambition linked to it.
2. Verify they appear in the Clarify screen.
3. Apply styling to differentiate Roles from Ambitions visually.

## Success Criteria
- [ ] Roles and Ambitions lists are visible and accurate.
- [ ] Users can navigate from empty state to a configured system within the TUI.
