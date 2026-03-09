# Implementation Plan: TUI Navigation & Refactor

## Phase 1: Structure & Componentization
1. Create `src/cli/main_tui.py` as the new entry point.
2. Refactor `src/cli/tui_capture.py` into a `CaptureView(Static)` component.
3. Refactor `src/cli/tui_inbox.py` into an `InboxListView(Static)` component.

## Phase 2: Main Application Skeleton
1. Implement a `MindWaterApp(App)` class.
2. Incorporate a `TabbedContent` or a sidebar layout.
3. Integrate the two views as tabs or screen contents.

## Phase 3: Navigation & Global State
1. Define global bindings (e.g., `Tab`, `Ctrl+C`, `Ctrl+L`) to toggle views.
2. Ensure consistent styling (CSS) across the app.
3. Handle refreshing the `InboxListView` when it is switched to.

## Phase 4: Testing & Final Polish
1. Run `python -m src.cli.main_tui` and verify navigation.
2. Verify that `tui_capture` logic correctly saves to Firebase.
3. Verify that `tui_inbox` logic correctly fetches from Firebase.
4. Clean up the standalone files if they are no longer needed (or keep them as legacy).

## Success Criteria
- [ ] Application has a unified navigation interface.
- [ ] Both Capture and List views are functional.
- [ ] User can switch views without crashing.
- [ ] App follows a modern, consistent aesthetic.
