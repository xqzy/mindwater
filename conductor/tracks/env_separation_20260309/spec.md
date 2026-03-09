# Spec: Environment Separation and Migration Mechanism

## Goal
To prevent accidental data loss in production by separating the production and development environments and providing a safe mechanism for migrating changes.

## Requirements
1. **Dual Database Configuration**:
    - **Production Database**: `gtd.db` (The user's live data).
    - **Development Database**: `gtd_dev.db` (The agent's workspace data).
2. **Environment Switching**:
    - The application must determine which database to use based on an environment variable (e.g., `APP_ENV`).
    - Default to `production` for normal user use, but allow `development` for agent tasks.
3. **Agent Constraint**:
    - The agent MUST NOT modify `gtd.db` directly.
    - All automated tests and development tasks must run against `gtd_dev.db`.
4. **Migration Mechanism**:
    - A script or tool to apply schema changes or verified data from `development` to `production`.
    - This should only be executed manually by the user or after explicit verification.
5. **Safety Checks**:
    - Prevent the agent from deleting or initializing `gtd.db` if it's not the intended target.

## Technical Implementation
- Update `src/database/session.py` to use `DATABASE_URL` based on `APP_ENV`.
- Implement a `migrate.py` script using SQLAlchemy/Alembic or a custom implementation for schema synchronization.
- Update tests to always use `gtd_dev.db` or an in-memory database.
