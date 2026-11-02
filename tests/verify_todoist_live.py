#!/usr/bin/env python3
"""
Mindwater Todoist Diagnostics & Automated Verification Engine.

Runs two suites:
1. Offline Mocked Suite: Executes all 42 unit & integration tests against an isolated in-memory database.
2. Live Todoist Connection Check (Read-Only): Uses the sticky token stored in gtd_dev.db to verify
   Todoist Unified API v1 connectivity (Projects, Labels, Active Tasks) without modifying remote data.
"""
import os
import subprocess
import sys

# Ensure project root (/app) is in sys.path when invoked as python tests/verify_todoist_live.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database.session import SessionLocal
from src.services.todoist import (
    get_todoist_token,
    mask_token,
    fetch_todoist_projects,
    fetch_todoist_labels,
    fetch_todoist_tasks,
)


def main():
    print("=" * 65)
    print("1. RUNNING AUTOMATED UNIT & INTEGRATION TEST SUITE (42 TESTS)")
    print("=" * 65)
    res = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "tests", "-v"],
        env={"APP_ENV": "test", "DATABASE_PATH": "/tmp/test_gtd.db", "PATH": "/usr/local/bin:/usr/bin:/bin"}
    )
    if res.returncode != 0:
        print("\n[FAIL] Unit test suite failed!")
        sys.exit(res.returncode)

    print("\n" + "=" * 65)
    print("2. RUNNING LIVE TODOIST UNIFIED API v1 DIAGNOSTIC (READ-ONLY)")
    print("=" * 65)
    db = SessionLocal()
    try:
        token = get_todoist_token(db)
        if not token:
            print("[SKIP] No Todoist API token configured in app_setting.")
            return

        print(f"Token found in DB : {mask_token(token)}")
        projects = fetch_todoist_projects(token)
        labels = fetch_todoist_labels(token)
        tasks = fetch_todoist_tasks(token)

        print(f"[OK] Todoist Projects fetched : {len(projects)} -> {[p.get('name') for p in projects]}")
        print(f"[OK] Todoist Labels fetched   : {len(labels)} -> {[l.get('name') for l in labels]}")
        print(f"[OK] Todoist Active Tasks     : {len(tasks)}")
        print("\n[SUCCESS] All automated tests and live Todoist API checks passed!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
