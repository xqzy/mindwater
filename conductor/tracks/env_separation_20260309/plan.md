# Plan: Environment Separation and Migration Mechanism

## Tasks
1. [ ] **Update Configuration**
    - [ ] Modify `src/database/session.py` to handle multiple database environments.
    - [ ] Add `APP_ENV` and `DATABASE_DEV_PATH` to `.env` file via `load_dotenv()`.
2. [ ] **Implement Environment Logic**
    - [ ] Ensure `init_db()` is scoped correctly and doesn't accidentally wipe data.
    - [ ] Add a confirmation or warning when running in production mode via CLI or TUI.
3. [ ] **Implement Migration Script**
    - [ ] Create `scripts/migrate.py` to handle schema migrations.
    - [ ] Add a backup mechanism for the production database before any migration.
4. [ ] **Test Separation**
    - [ ] Verify that automated tests only touch the development database.
    - [ ] Manually verify that production data remains intact during development tasks.
5. [ ] **Documentation**
    - [ ] Document how to switch environments and run migrations.
