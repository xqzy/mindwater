# Implementation Plan: Role-First Inbox Clarification & Quick Role/Ambition Creation

## Tasks
1. [x] **Inbox Header & Clarify Modal Layout (`src/api/static/index.html`, `src/api/static/style.css`)**
    - [x] Add `+ Add Role` and `+ Add Ambition` buttons to the `#inbox` tab header.
    - [x] Reorder `#clarify-modal` so **Role** (`#clarify-role`) comes first before **Project (Ambition)** (`#clarify-ambition`), and add inline `+ Add Role` / `+ Add Ambition` buttons.
    - [x] Ensure `#horizon-modal` stacks cleanly above `#clarify-modal` (`z-index: 1100`).
2. [x] **Dynamic Role -> Ambition Filtering & Modal Integration (`src/api/static/app.js`)**
    - [x] Implement `filterClarifyAmbitionsByRole(roleId, preselectedAmbitionId)` and bind it to `#clarify-role` `change`.
    - [x] Wire up `#inbox-add-role-btn`, `#inbox-add-ambition-btn`, `#clarify-add-role-btn`, and `#clarify-add-ambition-btn`.
    - [x] Update `horizonForm.onsubmit` so creating a Role or Ambition from the Inbox screen or Clarify modal refreshes options and auto-selects the new Role/Ambition.
3. [x] **Verification & Living Documentation**
    - [x] Run automated test suite (`python -m unittest discover tests -v`) to verify zero regressions.
    - [x] Update `conductor/product.md`, `conductor/tracks.md`, `plan.md`, and `metadata.json`.
