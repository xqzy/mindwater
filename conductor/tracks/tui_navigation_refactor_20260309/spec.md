# Specification: TUI Navigation & Refactor

## Overview
Refactor the standalone TUI scripts into a single, cohesive "MainApp". This will provide a centralized interface for the GTD system, allowing users to switch between "Capture" and "Inbox List" views seamlessly without restarting the application.

## Requirements

### 1. Main Application Structure
- A central `MainApp(App)` class in `src/cli/main_tui.py`.
- Use **Textual's** `TabbedContent` or a `Sidebar` for navigation.
- Support switching between views using the `Tab` key or a dedicated navigation menu.

### 2. Integrated Views
- **Capture View:** Port the logic from `src/cli/tui_capture.py` into a reusable component.
- **Inbox List View:** Port the logic from `src/cli/tui_inbox.py` into a reusable component.
- Ensure state (like the database connection or current list) is handled correctly during switches.

### 3. User Experience
- App starts on a "Dashboard" or the "Capture" view by default.
- Global keybindings for quick navigation (e.g., `Ctrl+C` for Capture, `Ctrl+L` for List).
- Consistent Header and Footer across all screens.

## Success Criteria
- [ ] Single entry point `python -m src.cli.main_tui` launches the full app.
- [ ] User can switch between Capture and Inbox List without exiting.
- [ ] Capture functionality works within the integrated view.
- [ ] Inbox List refreshes correctly when navigated to.
