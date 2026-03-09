# Implementation Plan: Todoist Task Push

## Tasks
1. [x] **Todoist Service Development**
    - [x] Create `src/services/todoist.py`.
    - [x] Implement `push_task_to_todoist(title, due_date)` using `httpx`.
    - [x] Handle API errors and token missing scenarios.
2. [x] **TUI Integration**
    - [x] Add `p` binding to `TasksView` in `src/cli/main_tui.py`.
    - [x] Implement `action_push_to_todoist` method in `TasksView`.
    - [x] Use `@work(thread=True)` for non-blocking API calls.
    - [x] Show notifications for success/failure.
3. [x] **Verification**
    - [x] Create a mock/test script to verify API logic without hitting real servers (using `httpx.MockTransport` or similar).
    - [x] Manual verification with a real API token in the `development` environment.
4. [x] **Documentation**
    - [x] Update `README` or track notes on how to configure the `TODOIST_API_TOKEN`.
