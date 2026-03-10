# Specification: TUI Horizon Refinement

## Overview
Improve the "Horizons" screen in the MindWater TUI to provide a more focused and informative experience. This includes hierarchical filtering, the ability to edit existing items, and detailed performance metrics for projects (Ambitions).

## Requirements

### 1. Hierarchical Filtering
- **Role Selection:** Selecting a Role in the "Roles" table must automatically filter the "Ambitions" table to show only those linked to the selected Role.
- **Ambition Selection:** Selecting an Ambition in the "Ambitions" table must filter the "Tasks" table to show only tasks belonging to that Ambition.
- **Clearance:** If no Role is selected, show all Ambitions (or a placeholder). If no Ambition is selected, the Tasks table should be empty.

### 2. Editing (Keystroke 'e')
- Add a new keyboard binding 'e' to the `HorizonsView`.
- When 'e' is pressed:
  - If a **Role** is focused/selected, open a modal to edit its name and description.
  - If an **Ambition** is focused/selected, open a modal to edit its outcome (name) and status.
- Changes must persist to the database and update the UI immediately.

### 3. Ambition Statistics
- When an Ambition is selected, display a "Statistics" panel (new component) with the following metrics:
  - **Total Hours Spent:** Sum of time recorded for all finished tasks associated with the Ambition.
  - **Recent Throughput (6 weeks):** Number of tasks completed in the last 6 weeks.
  - **Recent Throughput (2 weeks):** Number of tasks completed in the last 2 weeks.
  - **Other Metrics:** (Optional but encouraged) completion rate, average task duration, etc.

## User Workflow
1. User navigates to the "Horizons" tab (Ctrl+H).
2. User selects a Role (e.g., "Developer"). The "Ambitions" table updates to show only Developer-related projects.
3. User selects an Ambition (e.g., "Refactor TUI"). The "Tasks" table updates to show tasks for that project, and the "Statistics" panel displays metrics.
4. User presses 'e' while an Ambition is selected, updates the name, and the table refreshes.
