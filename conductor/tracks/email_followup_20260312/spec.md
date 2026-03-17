# Specification: Email Follow-up Screen

## Goal
Create a new TUI screen as the first tab to manage emails flagged for follow-up, allowing them to be converted into GTD actions or dismissed from the view.

## Requirements
- **First Tab**: The new "Follow-up" screen must be the very first tab in the top-tab bar.
- **Email Connection**:
    - Connect to a personal mailbox using IMAP.
    - Read-only access.
    - Fetch emails from the last 14 days that are flagged (e.g., `\Flagged` in IMAP).
- **Email Display**:
    - List emails with Subject, Sender, and Date.
    - Allow selecting an email to convert it into a GTD action.
    - Provide an option to "delete" (dismiss) from the screen without deleting it from the mailbox.
- **Action Creation**:
    - When converting to an action, prompt for:
        - Task Title (default to email subject).
        - Role (Area of Focus).
        - Ambition (Project, optional).
        - Energy Level.
        - (Context tags should be parsed or prompted if needed, but title/role/ambition are primary).

## Technical Details
- **Email Service**: Enhance `src/services/email_poller.py` or create a new `EmailFollowupService`.
- **IMAP Search**: Use `(SINCE "{date}" FLAGGED)` for search.
- **Data Persistence**: Since we shouldn't delete from mailbox, we need a way to track which emails have been "dismissed" locally. We could use a local SQLite table `dismissed_emails`.
- **TUI Component**: Create `FollowupView` in `src/cli/main_tui.py`.

## Success Criteria
- [ ] User can see flagged emails from the last 2 weeks in the first tab.
- [ ] User can convert an email to a task.
- [ ] User can dismiss an email from the list (it disappears from TUI but remains in mailbox).
- [ ] Task details are correctly prompted and saved to the local SQLite database.
