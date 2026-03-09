# Track: Todoist Task Push

**Status: Completed**

## Summary
Implemented the ability to push MindWater tasks to Todoist, preserving their titles and planned dates.

## Key Files
- `src/services/todoist.py`: The Todoist API service.
- `src/cli/main_tui.py`: Updated `TasksView` with the `p` binding.
- `verify_todoist.py`: Unit tests for the Todoist service.

## Verification
- Unit tests passed using mocked API responses.
- TUI integration verified visually (UI bindings and notification logic).
