import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from src.database.models import Base, Horizon2, Ambition, Task, Inbox
from src.database import crud
from src.api.main import app, get_db
from src.services.todoist import _fetch_paginated


class TestTodoistBidirectionalSync(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        Base.metadata.create_all(bind=self.engine)
        self.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.TestingSessionLocal()

        def override_get_db():
            db = self.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    @patch("src.api.main.fetch_todoist_projects")
    def test_sticky_token_storage_and_masking(self, mock_fetch_projects):
        mock_fetch_projects.return_value = [{"id": "p1", "name": "Inbox"}]

        # Save token via UI endpoint
        resp = self.client.post("/todoist/settings", json={"token": "secret_todoist_token_9876"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["configured"])
        self.assertTrue(data["connection_ok"])
        self.assertEqual(data["masked_token"], "••••••••••••9876")

        # Verify persisted in app_setting table
        settings_resp = self.client.get("/todoist/settings")
        self.assertEqual(settings_resp.status_code, 200)
        self.assertTrue(settings_resp.json()["configured"])
        self.assertEqual(settings_resp.json()["masked_token"], "••••••••••••9876")

    @patch("src.services.todoist.fetch_todoist_tasks")
    def test_sync_routing_and_two_way_completion(self, mock_fetch_tasks):
        # Configure sticky token
        self.client.post("/todoist/settings", json={"token": "test_token_1234"})

        # Create Role mapped to Todoist Project 'proj_dev' and Ambition mapped to Label 'mindwater_v2'
        role = crud.create_h2(self.db, name="Developer")
        self.client.post("/todoist/mappings/role", json={
            "role_id": role.id,
            "todoist_project_id": "proj_dev",
            "todoist_project_name": "Developer"
        })

        amb = crud.create_ambition(
            self.db,
            outcome="Mindwater v2",
            h2_id=role.id,
            todoist_label_id="lbl_1",
            todoist_label_name="mindwater_v2"
        )

        # Create an existing local synced task that is no longer in Todoist's active tasks (completed in Todoist)
        completed_in_todoist_task = crud.create_task(
            self.db,
            title="Finish database schema",
            ambition_id=amb.id,
            role_id=role.id,
            estimated_time=45,
            todoist_task_id="td_completed_1"
        )

        # Mock remote Todoist active tasks:
        # 1. Task with mapped label 'mindwater_v2' and 30m duration -> should go straight to Tasks
        # 2. Unmapped urgent task -> should go to Inbox
        mock_fetch_tasks.return_value = [
            {
                "id": "td_mapped_100",
                "content": "Write API unit tests",
                "project_id": "proj_other",
                "labels": ["mindwater_v2"],
                "priority": 4,
                "due": {"date": "2026-11-02"},
                "duration": {"amount": 30, "unit": "minute"},
                "created_at": "2026-11-01T10:00:00Z"
            },
            {
                "id": "td_unmapped_200",
                "content": "Buy milk on the way home",
                "project_id": "proj_inbox",
                "labels": [],
                "priority": 1,
                "due": None,
                "duration": None,
                "created_at": "2026-11-02T08:00:00Z"
            }
        ]

        sync_resp = self.client.post("/todoist/sync")
        self.assertEqual(sync_resp.status_code, 200)
        summary = sync_resp.json()
        self.assertEqual(summary["imported_tasks"], 1)
        self.assertEqual(summary["imported_inbox"], 1)
        self.assertEqual(summary["completed_tasks"], 1)

        # Verify mapped task went to Tasks with duration, priority, due date, and Ambition/Role links
        self.db.expire_all()
        mapped_task = self.db.query(Task).filter(Task.todoist_task_id == "td_mapped_100").first()
        self.assertIsNotNone(mapped_task)
        self.assertEqual(mapped_task.title, "Write API unit tests")
        self.assertEqual(mapped_task.ambition_id, amb.id)
        self.assertEqual(mapped_task.role_id, role.id)
        self.assertEqual(mapped_task.estimated_time, 30)
        self.assertEqual(mapped_task.todoist_priority, 4)
        self.assertEqual(mapped_task.todoist_due_date, "2026-11-02")

        # Verify unmapped task went to Inbox
        inbox_item = self.db.query(Inbox).filter(Inbox.todoist_task_id == "td_unmapped_200").first()
        self.assertIsNotNone(inbox_item)
        self.assertEqual(inbox_item.raw_text, "Buy milk on the way home")
        self.assertEqual(inbox_item.source_tag, "todoist")

        # Verify task completed in Todoist was marked done locally and credited estimated_time
        done_task = self.db.query(Task).filter(Task.id == completed_in_todoist_task.id).first()
        self.assertEqual(done_task.status, "done")
        self.assertIsNotNone(done_task.completed_at)
        self.assertEqual(done_task.actual_time, 45)

    @patch("src.services.todoist.update_todoist_task")
    def test_clarify_todoist_inbox_item_in_place(self, mock_update_todoist):
        self.client.post("/todoist/settings", json={"token": "test_token_1234"})
        role = crud.create_h2(self.db, name="Home", h4_id=None)
        amb = crud.create_ambition(
            self.db,
            outcome="Kitchen Renovation",
            h2_id=role.id,
            todoist_label_name="kitchen_reno"
        )
        inbox_item = crud.create_inbox_item(
            self.db,
            raw_text="Call contractor",
            source_tag="todoist",
            todoist_task_id="td_inbox_555",
            todoist_due_date="2026-11-05",
            todoist_priority=4
        )

        inbox_item_id = inbox_item.id
        mock_update_todoist.return_value = {"id": "td_inbox_555"}

        resp = self.client.post(f"/inbox/{inbox_item_id}/clarify", json={
            "type": "task",
            "title": "Call contractor for quote",
            "role_id": role.id,
            "ambition_id": amb.id,
            "energy_level": "High",
            "estimated_time": 20,
            "context_tags": ["@calls"]
        })
        self.assertEqual(resp.status_code, 200)

        # Inbox item should be deleted and Task created with same todoist_task_id
        self.db.expire_all()
        self.assertIsNone(self.db.query(Inbox).filter(Inbox.id == inbox_item_id).first())
        clarified_task = self.db.query(Task).filter(Task.todoist_task_id == "td_inbox_555").first()
        self.assertIsNotNone(clarified_task)
        self.assertEqual(clarified_task.title, "Call contractor for quote")
        self.assertEqual(clarified_task.estimated_time, 20)
        mock_update_todoist.assert_called_once()

    @patch("src.api.main.close_todoist_task")
    def test_mark_done_in_mindwater_closes_in_todoist(self, mock_close):
        self.client.post("/todoist/settings", json={"token": "test_token_1234"})
        task = crud.create_task(self.db, title="Synced Task", todoist_task_id="td_999")

        resp = self.client.patch(f"/tasks/{task.id}/status?status=done")
        self.assertEqual(resp.status_code, 200)
        mock_close.assert_called_once_with("test_token_1234", "td_999")

    @patch("src.services.todoist.push_task_to_todoist")
    def test_batch_push_and_stale_todoist_tasks(self, mock_push):
        self.client.post("/todoist/settings", json={"token": "test_token_1234"})
        mock_push.side_effect = ["td_batch_1", "td_batch_2"]

        t1 = crud.create_task(self.db, title="Weekly Action 1", estimated_time=15)
        t2 = crud.create_task(self.db, title="Weekly Action 2", estimated_time=25)
        stale_t = crud.create_task(
            self.db,
            title="Old Stale Todoist Task",
            todoist_task_id="td_old_1",
            todoist_created_at=datetime.now(UTC) - timedelta(days=20)
        )

        # Test batch push (Idea #2)
        batch_resp = self.client.post("/tasks/batch-push-todoist", json={"task_ids": [t1.id, t2.id]})
        self.assertEqual(batch_resp.status_code, 200)
        self.assertEqual(batch_resp.json()["pushed_count"], 2)

        # Test stale tasks endpoint (Idea #10)
        stale_resp = self.client.get("/review/stale-todoist-tasks")
        self.assertEqual(stale_resp.status_code, 200)
        stale_list = stale_resp.json()
        self.assertEqual(len(stale_list), 1)
        self.assertEqual(stale_list[0]["id"], stale_t.id)

    def test_todoist_unified_api_v1_pagination_envelope(self):
        # Verify _fetch_paginated handles Todoist Unified API v1 {'results': [...], 'next_cursor': ...}
        mock_client = MagicMock()
        resp1 = MagicMock()
        resp1.json.return_value = {"results": [{"id": "p1", "name": "Inbox"}], "next_cursor": "cur_2"}
        resp2 = MagicMock()
        resp2.json.return_value = {"results": [{"id": "p2", "name": "Work"}], "next_cursor": None}
        mock_client.get.side_effect = [resp1, resp2]

        items = _fetch_paginated(mock_client, "https://api.todoist.com/api/v1/projects", {"Authorization": "Bearer tok"})
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["name"], "Inbox")
        self.assertEqual(items[1]["name"], "Work")

    @patch("src.services.todoist.fetch_todoist_projects")
    @patch("src.services.todoist.fetch_todoist_tasks")
    def test_sync_filters_welcome_archived_and_completed_tasks_and_cleans_inbox(self, mock_fetch_tasks, mock_fetch_projects):
        self.client.post("/todoist/settings", json={"token": "test_token_1234"})

        # Seed a previously imported 'Welcome' onboarding task in Inbox that should be cleaned up on sync
        crud.create_inbox_item(
            self.db,
            raw_text="You can add subtasks here! ✅",
            source_tag="todoist",
            todoist_task_id="td_welcome_subtask"
        )

        mock_fetch_projects.return_value = [
            {"id": "proj_inbox", "name": "Inbox", "is_archived": False, "is_deleted": False},
            {"id": "proj_welcome", "name": "Welcome 👋", "is_archived": False, "is_deleted": False},
            {"id": "proj_archived", "name": "Old Project", "is_archived": True, "is_deleted": False},
        ]

        mock_fetch_tasks.return_value = [
            {
                "id": "td_welcome_subtask",
                "content": "You can add subtasks here! ✅",
                "project_id": "proj_welcome",
                "checked": False,
                "is_deleted": False
            },
            {
                "id": "td_archived_proj_task",
                "content": "Task in archived project",
                "project_id": "proj_archived",
                "checked": False,
                "is_deleted": False
            },
            {
                "id": "td_checked_task",
                "content": "Already checked task",
                "project_id": "proj_inbox",
                "checked": True,
                "is_deleted": False
            },
            {
                "id": "td_valid_task",
                "content": "Real active inbox task",
                "project_id": "proj_inbox",
                "checked": False,
                "is_deleted": False
            }
        ]

        sync_resp = self.client.post("/todoist/sync")
        self.assertEqual(sync_resp.status_code, 200)
        summary = sync_resp.json()
        self.assertEqual(summary["imported_inbox"], 1)

        # Verify only 'Real active inbox task' is in Inbox, and 'You can add subtasks here! ✅' was removed
        self.db.expire_all()
        inbox_items = crud.get_inbox_items(self.db)
        self.assertEqual(len(inbox_items), 1)
        self.assertEqual(inbox_items[0].raw_text, "Real active inbox task")


if __name__ == "__main__":
    unittest.main()
