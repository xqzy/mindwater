# Spec: Task Details Editing

## Objective
Enable users to modify all details of a structured GTD task in the local SQLite database.

## Requirements
- Edit Title
- Edit Status (todo, in_progress, done)
- Edit Role (H2) and Ambition (H1) links
- Edit Context Tags (list of strings)
- Edit Energy Level (Low, Medium, High)
- Edit Planned Date (defer/scheduled date)
- Edit Estimated Time (in minutes)

## Data Model Changes
- Add `planned_date` (DateTime) to `Task` model in SQLite.
- Add `estimated_time` (Integer) to `Task` model in SQLite.
- Update `Task` dataclass in `src/models/gtd.py`.

## UI Requirements
- New `TaskEditScreen` with inputs for all fields.
- Keybinding in `TasksView` to trigger editing of the selected task.
- Form validation for date and numeric inputs.
- Refresh tasks list after saving changes.
