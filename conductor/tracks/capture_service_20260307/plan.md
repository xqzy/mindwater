# Implementation Plan - Track: Capture Service & Email Processing

## Phase 1: Research & Strategy
- [x] Task: Research IMAP libraries in Python (`imaplib` or similar) and FastAPI request handling.
- [x] Task: Define the Regex/Heuristics patterns for extracting context tags.
- [x] Task: Plan the architecture for the background email polling script.

## Phase 2: Parsing Engine (TDD)
- [x] Task: Implement text parser.
    - [x] Write unit tests for parsing #tags, @contexts, and stripping email signatures.
    - [x] Implement the parsing logic.
    - [x] Verify tests pass.

## Phase 3: Core Capture Service & API (TDD)
- [x] Task: Implement Capture API.
    - [x] Write unit tests for the HTTP POST endpoint simulating capture inputs.
    - [x] Implement the FastAPI endpoint that uses the Parsing Engine and saves to the `Inbox` table.
    - [x] Verify tests pass.

## Phase 4: Email Ingestion (IMAP) (TDD)
- [x] Task: Implement IMAP Poller.
    - [x] Write unit tests (with mocked IMAP) for fetching unread emails and extracting body/subject.
    - [x] Implement the IMAP connection, fetching, and marking as read logic.
    - [x] Integrate with the Parsing Engine and `Inbox` table persistence.
    - [x] Verify tests pass.

## Phase 5: CLI Command
- [x] Task: Implement CLI entry point.
    - [x] Write unit tests for a local CLI command wrapper.
    - [x] Implement the CLI script that sends input to the Capture service.
    - [x] Verify tests pass.

## Phase 6: Integration & Validation
- [x] Task: Integration Tests
    - [x] Write tests to verify the end-to-end flow from API/Email/CLI to the SQLite database.
- [x] Task: Quality Audit
    - [x] Perform a code review for security (credential handling) and efficiency.
    - [x] Run linting and type checks.

## Phase: Review Fixes
- [x] Task: Apply review suggestions ef0cbb8
