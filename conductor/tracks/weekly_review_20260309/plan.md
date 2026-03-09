# Implementation Plan: GTD Weekly Review Module

## Phase 1: Database Support
1. Add `ReviewLog` model to `src/database/models.py` (id, timestamp).
2. Add `record_review(db)` function to `src/database/crud.py`.
3. Run `init_db()` automatically on app start (already done).

## Phase 2: Review Wizard UI
1. Create `ReviewView(Static)` component in `src/cli/main_tui.py`.
2. Use `ContentSwitcher` or a similar mechanism to cycle through review steps.
3. Implement "Next" and "Back" buttons.

## Phase 3: Step Implementation
1. **Mind Dump:** Use a `TextArea` or `Input` that repeatedly saves items until the user is done.
2. **Project Review:** Fetch all active Ambitions and display them with buttons to change status or "Add Task".
3. **Completion:** Show a summary and the "Finish" button.

## Phase 4: Integration
1. Add the "Review" tab to `MindWaterApp`.
2. Add `Ctrl+R` navigation binding (and move existing `R` refresh to `F5` or similar if needed).

## Phase 5: Testing
1. Conduct a full review process and verify project status updates and review logging.

## Success Criteria
- [ ] Guided review workflow functions without errors.
- [ ] Database updates correctly based on review actions.
