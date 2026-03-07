# Specification - Track: Implement SQLite Database Schema and Core CRUD Functions

## Overview
Implement the database persistence layer using SQLite and SQLAlchemy (ORM) to store and manage the core GTD data models: Roles, Ambitions, and Tasks. This track includes setting up the database connection, defining the SQLAlchemy models, and implementing the core CRUD (Create, Read, Update, Delete) operations with filtered listing capabilities.

## Functional Requirements
- **Database Connection:** Configure a local SQLite file (e.g., `gtd.db`) for persistent storage.
- **SQLAlchemy Models:** Define ORM models for:
  - `Horizon5` (Purpose)
  - `Horizon4` (Vision)
  - `Horizon2` (Roles)
  - `Ambition` (Projects)
  - `Task` (Next Actions)
  - `Inbox` (Capture)
- **Schema Management:** Set up Alembic to manage database migrations and ensure schema versioning.
- **Core CRUD Operations:**
  - Standard CRUD (Create, Read, Update, Delete) for all models.
  - Filtered Listing:
    - List `Ambitions` by `Role` (H2).
    - List `Tasks` by `Ambition` (H1) or `Role` (H2).
    - Filter `Tasks` by `Context Tags` and `Energy Level`.
- **Empty Role Check:** Implement a helper function/query to identify `Roles` with no active `Ambitions` or `Tasks`.

## Non-Functional Requirements
- **Data Integrity:** Use foreign key constraints to maintain relationships between horizons.
- **Maintainability:** Use SQLAlchemy's modern `declarative_base` and session management patterns.

## Acceptance Criteria
- Database file is created and connection is verified.
- Alembic is configured, and the initial migration successfully creates the schema.
- Unit tests verify all CRUD operations and filtering logic.
- Integration tests confirm the full hierarchy is stored and retrieved correctly.

## Out of Scope
- Frontend implementation.
- External Todoist bi-directional sync.
