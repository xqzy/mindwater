import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.database.models import Base, Horizon2, Ambition, Task
from src.database.session import get_db


class TestTaskLifecycle(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        def override_get_db():
            db = self.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

        db = self.TestingSessionLocal()
        role = Horizon2(name="Developer", description="Code")
        db.add(role)
        db.commit()
        db.refresh(role)
        amb = Ambition(outcome="Ship Feature", h2_id=role.id)
        db.add(amb)
        db.commit()
        db.refresh(amb)
        t1 = Task(title="Write Tests", role_id=role.id, ambition_id=amb.id, status="todo")
        t2 = Task(title="Obsolete Chore", role_id=role.id, ambition_id=amb.id, status="todo")
        db.add_all([t1, t2])
        db.commit()
        db.refresh(t1)
        db.refresh(t2)
        self.role_id = role.id
        self.amb_id = amb.id
        self.t1_id = t1.id
        self.t2_id = t2.id
        db.close()

    def tearDown(self):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_mark_done_hides_by_default_and_shows_with_include_completed(self):
        # Initially both active tasks are returned
        tasks = self.client.get("/tasks").json()
        self.assertEqual(len(tasks), 2)

        # Mark task 1 as done (finalised)
        res = self.client.patch(f"/tasks/{self.t1_id}/status?status=done")
        self.assertEqual(res.status_code, 200)

        # By default (include_completed=false), only active todo tasks are returned
        active_tasks = self.client.get("/tasks").json()
        self.assertEqual(len(active_tasks), 1)
        self.assertEqual(active_tasks[0]["id"], self.t2_id)

        # With include_completed=true, both active and finalised tasks are returned
        all_tasks = self.client.get("/tasks?include_completed=true").json()
        self.assertEqual(len(all_tasks), 2)
        statuses = {t["id"]: t["status"] for t in all_tasks}
        self.assertEqual(statuses[self.t1_id], "done")
        self.assertEqual(statuses[self.t2_id], "todo")

    def test_delete_task_permanently(self):
        del_res = self.client.delete(f"/tasks/{self.t2_id}")
        self.assertEqual(del_res.status_code, 200)

        remaining = self.client.get("/tasks?include_completed=true").json()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["id"], self.t1_id)

    def test_monitoring_status_and_filtering(self):
        # Change task 2 status to monitoring
        res = self.client.patch(f"/tasks/{self.t2_id}/status?status=monitoring")
        self.assertEqual(res.status_code, 200)

        # Default GET /tasks returns both todo and monitoring open tasks
        open_tasks = self.client.get("/tasks").json()
        self.assertEqual(len(open_tasks), 2)

        # Filter only monitoring tasks
        monitoring_only = self.client.get("/tasks?status_filter=monitoring").json()
        self.assertEqual(len(monitoring_only), 1)
        self.assertEqual(monitoring_only[0]["id"], self.t2_id)
        self.assertEqual(monitoring_only[0]["status"], "monitoring")

        # Filter only todo tasks
        todo_only = self.client.get("/tasks?status_filter=todo").json()
        self.assertEqual(len(todo_only), 1)
        self.assertEqual(todo_only[0]["id"], self.t1_id)

        # Ambition task counts count monitoring tasks as open (not stalled)
        ambitions = self.client.get("/ambitions").json()
        self.assertEqual(ambitions[0]["todo_count"], 2)
        self.assertEqual(ambitions[0]["monitoring_count"], 1)

    def test_snooze_task_for_todo_and_monitoring(self):
        # Snooze a normal todo task
        s1 = self.client.post(f"/tasks/{self.t1_id}/snooze", json={"due_date": "2026-12-01"})
        self.assertEqual(s1.status_code, 200)
        self.assertEqual(s1.json()["due_date"], "2026-12-01")

        # Switch task 2 to monitoring and snooze it too
        self.client.patch(f"/tasks/{self.t2_id}/status?status=monitoring")
        s2 = self.client.post(f"/tasks/{self.t2_id}/snooze", json={"due_date": "2026-12-15"})
        self.assertEqual(s2.status_code, 200)
        self.assertEqual(s2.json()["due_date"], "2026-12-15")

        # Clear due date on task 1
        s_clear = self.client.post(f"/tasks/{self.t1_id}/snooze", json={"due_date": ""})
        self.assertEqual(s_clear.status_code, 200)
        self.assertIsNone(s_clear.json()["due_date"])

    def test_horizons_ambition_tasks_and_editing(self):
        detail_tasks = self.client.get(f"/ambitions/{self.amb_id}/tasks").json()
        self.assertEqual(len(detail_tasks), 2)
        first = detail_tasks[0]
        self.assertEqual(first["role_id"], self.role_id)
        self.assertEqual(first["ambition_id"], self.amb_id)

        # Edit task from Horizons details (updating title, status to monitoring, and due_date)
        upd = self.client.put(
            f"/tasks/{self.t1_id}",
            json={
                "title": "Updated from Horizons",
                "status": "monitoring",
                "due_date": "2026-11-30",
                "energy_level": "High",
                "estimated_time": 45,
                "context_tags": ["@office"],
            },
        )
        self.assertEqual(upd.status_code, 200)

        refreshed = self.client.get(f"/ambitions/{self.amb_id}/tasks").json()
        edited = next(t for t in refreshed if t["id"] == self.t1_id)
        self.assertEqual(edited["title"], "Updated from Horizons")
        self.assertEqual(edited["status"], "monitoring")
        self.assertEqual(edited["due_date"], "2026-11-30")
        self.assertEqual(edited["context_tags"], ["@office"])


if __name__ == "__main__":
    unittest.main()

