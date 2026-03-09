# Specification: GTD Weekly Review Module

## Overview
Implement a guided "Weekly Review" module. In GTD, the Weekly Review is the "critical success factor" that ensures the system remains trusted and up-to-date. This track will provide a step-by-step TUI interface to help users get clear, current, and creative.

## Requirements

### 1. Weekly Review Wizard
- A new "Review" tab or a modal process.
- Step-by-step navigation (Next/Back).

### 2. Review Steps
- **Step 1: Mind Dump:** A large text area to capture all current "open loops". These should be saved to the Firebase Inbox.
- **Step 2: Inbox Clearing:** Integration with the existing Inbox view to process remaining items.
- **Step 3: Review Projects (Ambitions):** 
    - Display each active Ambition one by one.
    - User must confirm if it's still active or should be changed (On Hold, Completed).
    - Ensure every Ambition has at least one "Next Action".
- **Step 4: Review Calendar/Waiting For:** (Placeholder or basic list for now).
- **Step 5: Review Roles (Horizon 2):** Briefly display each role to see if anything new is needed.

### 3. Review Completion
- A final "Complete Review" button.
- Record the completion date in the local database (might need a new model for `ReviewLog`).

## Success Criteria
- [ ] Users can start a guided Weekly Review.
- [ ] Users can capture new items during the review.
- [ ] Users can review and update all active Ambitions (Projects).
- [ ] The system records the date of the last review.
