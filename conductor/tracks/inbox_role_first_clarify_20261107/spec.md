# Specification: Role-First Inbox Clarification & Quick Role/Ambition Creation from Inbox

## Goal
Improve the Inbox planning/clarification workflow so that:
1. Users select the **Role** first when clarifying an Inbox item, and the **Project (Ambition)** dropdown dynamically filters to show only ambitions belonging to that chosen Role.
2. Users can create a new **Role** or **Ambition (Project)** directly from the **Inbox** screen (both from the Inbox header toolbar and inline inside the Clarify modal).

## Requirements

### 1. Role-First Sequence in Clarify Modal (`#clarify-modal`)
- Move the **Role** selector (`#clarify-role`) above the **Project (Ambition)** selector (`#clarify-ambition`) in `#clarify-modal` (`src/api/static/index.html`).
- When `#clarify-role` changes:
  - Filter `#clarify-ambition` (`filterClarifyAmbitionsByRole`) so only active ambitions matching the selected `role_id` are listed (along with the default `None (Standalone Task)` option).
  - If no Role is selected (`""`), only show `None (Standalone Task — select a Role to see its projects)` (plus any unassigned ambitions with `role_id == null`).

### 2. Add Role or Ambition from Inbox (`#inbox` & `#clarify-modal`)
- **Inbox Screen Header (`#inbox`)**:
  - Add `+ Add Role` (`#inbox-add-role-btn`) and `+ Add Ambition` (`#inbox-add-ambition-btn`) buttons in the Inbox header bar (`src/api/static/index.html`) so users can add a Role or Ambition directly from the Inbox screen without switching tabs.
- **Clarify Modal Quick-Add Buttons (`#clarify-modal`)**:
  - Add inline `+ New Role` and `+ New Project` buttons next to the **Role** and **Project (Ambition)** labels inside `#clarify-modal`.
  - Clicking `+ New Project` inside `#clarify-modal` pre-populates `#ambition-role-select` with the currently selected Role in `#clarify-role`.
  - Saving a Role or Ambition in `#horizon-modal` while on the Inbox screen refreshes the Roles and Ambitions lists and automatically selects the newly created Role/Ambition in `#clarify-modal` if it is open.

## Non-Regressions
- Clarifying an Inbox item as either a `Next Action` (`task`) or a `Project` (`ambition`) continues to work identically with the backend (`POST /inbox/{item_id}/clarify`).
- Closing `#horizon-modal` when opened on top of `#clarify-modal` leaves `#clarify-modal` open with the newly created Role/Ambition selected.

