# Implementation Plan - Track: GTD Core Models (v2)

## Phase 1: Research & Strategy
- [x] Task: Research database design for deep hierarchical models (H5 down to H0).
- [x] Task: Define the unified schema for Horizons, Ambitions, and Tasks.
- [x] Task: Plan the logic for "Empty Role Flagging."

## Phase 2: Implementation (TDD)
- [x] Task: Horizon Models (H5, H4, H2)
    - [x] Write unit tests for Purpose, Vision, and Role model creation.
    - [x] Implement models with specified attributes (Name, Description, Icon, etc.).
    - [x] Verify tests pass.
- [x] Task: Ambition Model (H1)
    - [x] Write unit tests for Ambition linkage to H2/H4/H5.
    - [x] Implement Ambition model with Outcome and Status.
    - [x] Verify tests pass.
- [x] Task: Task Model (H0)
    - [x] Write unit tests for Task attributes (Title, Context Tags, Energy Level).
    - [x] Implement Task model with flexible linkage to Ambition or Role.
    - [x] Verify tests pass.
- [x] Task: Inbox Model (Capture)
    - [x] Write unit tests for frictionless Capture entry.
    - [x] Implement Inbox model (Raw Text, Source Tag, Timestamp).
    - [x] Verify tests pass.

## Phase 3: Validation & Quality Checks
- [x] Task: Integration Testing
    - [x] Write tests to verify the full hierarchy (H5 -> H4 -> H2 -> H1 -> H0).
    - [x] Test the "Empty Role Flagging" logic.
- [x] Task: Quality Audit
    - [x] Perform a code review for idiomatic patterns and security best practices.
    - [x] Run linting and type checks.
