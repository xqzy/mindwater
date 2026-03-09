# Implementation Plan: Weekly Review Polish & H2 Constraints

## Phase 1: Backend Logic
1. Update `src/database/crud.py`:
   - Add `get_roles_with_ambition_counts(db)` to easily identify roles without projects.
   - Add `get_ambitions_with_task_counts(db)` to identify projects without next actions.

## Phase 2: ReviewView UI Expansion
1. Modify `ReviewView` in `src/cli/main_tui.py`:
   - Add `step_roles` to the `ContentSwitcher`.
   - Update `steps` list to include `step_roles`.
   - Implement the visual flagging for roles with 0 ambitions.

## Phase 3: Interactive Actions in Review
1. Add "Add Next Action" button logic to the projects review step.
2. Add "Add Ambition" button logic to the roles review step.
3. Ensure these buttons open the existing `AddAmbitionScreen` or a simplified version.

## Phase 4: Final Summary
1. Update `step_finish` to display dynamic counts of captured items and updated projects.

## Phase 5: Testing
1. Verify the constraint flagging works by creating a Role with no Projects and running the review.
2. Verify adding tasks/projects during review correctly updates the counts.

## Success Criteria
- [ ] Users are guided through Role review.
- [ ] Stagnant life areas (Roles with no Projects) are brought to the user's attention.
- [ ] Review process is more interactive and helpful.
