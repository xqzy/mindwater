# Implementation Plan - Track: Implement SQLite Database Schema and Core CRUD Functions

## Phase 1: Research & Strategy
- [ ] Task: Research SQLAlchemy session management and async/sync trade-offs for SQLite.
- [ ] Task: Define the unified schema and relationships (H5 down to H0).
- [ ] Task: Plan the Alembic migration directory structure.

## Phase 2: Scaffolding & Configuration (TDD)
- [ ] Task: Database Scaffolding
    - [ ] Set up the SQLAlchemy connection and session factory.
    - [ ] Initialize Alembic and configure it for the project.
    - [ ] Create the initial migration script.
    - [ ] Verify database connection and schema creation in tests.

## Phase 3: Implementation (TDD)
- [ ] Task: CRUD for Horizons (H5, H4, H2)
    - [ ] Write unit tests for CRUD on Purpose, Vision, and Role.
    - [ ] Implement CRUD functions using SQLAlchemy.
    - [ ] Verify tests pass.
- [ ] Task: CRUD for Ambition (H1)
    - [ ] Write unit tests for CRUD on Ambition and linkage to H2/H4/H5.
    - [ ] Implement CRUD functions for Ambition.
    - [ ] Verify tests pass.
- [ ] Task: CRUD for Task (H0)
    - [ ] Write unit tests for CRUD on Task and linkage to H1/H2.
    - [ ] Implement CRUD functions for Task.
    - [ ] Verify tests pass.
- [ ] Task: Filtered Listing Logic
    - [ ] Write unit tests for filtered listing (by context, energy, and relationships).
    - [ ] Implement filtered query logic.
    - [ ] Verify tests pass.

## Phase 4: Validation & Quality Checks
- [ ] Task: Integration Testing
    - [ ] Write integration tests to verify data persistence across a full lifecycle.
    - [ ] Test the "Empty Role Flagging" helper function.
- [ ] Task: Quality Audit
    - [ ] Perform a code review for security and efficiency.
    - [ ] Run linting and type checks.
