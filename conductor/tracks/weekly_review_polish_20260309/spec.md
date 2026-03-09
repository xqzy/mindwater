# Specification: Weekly Review Polish & H2 Constraints

## Overview
Enhance the Weekly Review module to include the "Role Review" step and implement the product constraint where users are flagged if a Role has no active projects (Ambitions). This ensures all Areas of Focus are being maintained.

## Requirements

### 1. Enhanced Project Review
- During the Project Review step, add a button to "Add Next Action" directly for an Ambition if it has none.
- Visual indicator if an Ambition has no associated tasks with status "todo".

### 2. Role Review Step (Horizon 2)
- New Step in the wizard: **Review Roles**.
- Display each Role from the local database.
- **Constraint Check:** If a Role has zero active Ambitions, highlight it in RED and prompt the user: "This Area of Focus has no active projects. Would you like to create one?"
- Provide an "Add Ambition" button directly in this step.

### 3. Summary Step
- Show a final summary of what was changed during the review:
    - Number of items captured.
    - Number of projects updated.
    - Number of new projects created.

## Success Criteria
- [ ] Weekly Review includes a "Review Roles" step.
- [ ] Roles without projects are visually flagged as required by product goals.
- [ ] User can create projects directly from the Role Review step.
