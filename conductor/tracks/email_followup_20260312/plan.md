# Plan: Email Follow-up Screen

## Phase 1: Research & Preparation
- [ ] Verify IMAP credentials and connection settings.
- [ ] Define environment variables for email (EMAIL_USER, EMAIL_PASSWORD, EMAIL_IMAP_HOST).

## Phase 2: Core Logic Implementation
- [ ] Create a local SQLite model for `DismissedEmail` to track dismissed emails by Message-ID or UID.
- [ ] Implement `get_flagged_emails()` in `src/services/email_poller.py` or a new service.
    - [ ] Fetch emails from the last 14 days with the `\Flagged` flag.
    - [ ] Filter out emails that are already in the `DismissedEmail` table or already converted to tasks.
- [ ] Update `src/database/crud.py` to handle the new `DismissedEmail` model.

## Phase 3: TUI Integration
- [ ] Create `FollowupView` widget in `src/cli/main_tui.py`.
    - [ ] Add a `DataTable` to display emails.
    - [ ] Add a "Refresh" action to fetch emails.
- [ ] Create `EmailClarifyScreen` (or reuse/adapt `InboxClarifyScreen`) to prompt for task details.
- [ ] Update `MindWaterApp` in `src/cli/main_tui.py`:
    - [ ] Add the "Follow-up" tab as the first tab in `compose()`.
    - [ ] Register new bindings (e.g., `ctrl+f` for Follow-up).

## Phase 4: Validation
- [ ] Write a test case in `tests/test_email.py` for fetching flagged emails.
- [ ] Verify the TUI flow: list -> select -> clarify -> save -> disappear.
- [ ] Verify the "dismiss" flow: list -> dismiss -> disappear.
- [ ] Ensure that no emails are deleted from the mailbox.
