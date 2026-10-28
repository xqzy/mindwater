import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from src.database.models import Base, Ambition, Task
from src.database import crud
from src.api.main import app, get_db


class TestProjectRemoveAndArchive(unittest.TestCase):
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

    def test_delete_ambition_cascades_tasks(self):
        role = crud.create_h2(self.db, name="Developer")
        amb1 = crud.create_ambition(self.db, outcome="Project To Delete", h2_id=role.id)
        amb2 = crud.create_ambition(self.db, outcome="Project To Keep", h2_id=role.id)

        crud.create_task(self.db, title="Task 1 for Amb 1", ambition_id=amb1.id, role_id=role.id)
        crud.create_task(self.db, title="Task 2 for Amb 1", ambition_id=amb1.id, role_id=role.id)
        kept_task = crud.create_task(self.db, title="Task for Amb 2", ambition_id=amb2.id, role_id=role.id)

        response = self.client.delete(f"/ambitions/{amb1.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        # Verify Ambition 1 and its tasks are permanently deleted
        self.assertIsNone(crud.get_ambition(self.db, amb1.id))
        self.assertEqual(len(crud.get_tasks_by_ambition(self.db, amb1.id)), 0)

        # Verify Ambition 2 and its task remain untouched
        self.assertIsNotNone(crud.get_ambition(self.db, amb2.id))
        remaining_tasks = crud.get_all_tasks(self.db)
        self.assertEqual(len(remaining_tasks), 1)
        self.assertEqual(remaining_tasks[0].id, kept_task.id)

    def test_archive_ambition_cascades_tasks_and_filters_views(self):
        role = crud.create_h2(self.db, name="Developer")
        amb1 = crud.create_ambition(self.db, outcome="Project To Archive", h2_id=role.id)
        amb2 = crud.create_ambition(self.db, outcome="Active Project", h2_id=role.id)

        t1 = crud.create_task(self.db, title="Archived Task 1", ambition_id=amb1.id, role_id=role.id)
        t2 = crud.create_task(self.db, title="Archived Task 2", ambition_id=amb1.id, role_id=role.id)
        t_active = crud.create_task(self.db, title="Active Task", ambition_id=amb2.id, role_id=role.id)

        response = self.client.post(f"/ambitions/{amb1.id}/archive")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        # Verify database statuses are updated to 'archived'
        self.db.expire_all()
        archived_amb = crud.get_ambition(self.db, amb1.id)
        self.assertEqual(archived_amb.status, "archived")
        amb1_tasks = crud.get_tasks_by_ambition(self.db, amb1.id)
        self.assertEqual(len(amb1_tasks), 2)
        for task in amb1_tasks:
            self.assertEqual(task.status, "archived")

        # Verify GET /ambitions returns only active projects by default
        active_ambs = self.client.get("/ambitions").json()
        self.assertEqual(len(active_ambs), 1)
        self.assertEqual(active_ambs[0]["id"], amb2.id)

        # Verify GET /ambitions?status=archived returns the archived project with archived_count=2
        archived_ambs = self.client.get("/ambitions?status=archived").json()
        self.assertEqual(len(archived_ambs), 1)
        self.assertEqual(archived_ambs[0]["id"], amb1.id)
        self.assertEqual(archived_ambs[0]["archived_count"], 2)

        # Verify GET /tasks excludes archived tasks by default
        default_tasks = self.client.get("/tasks").json()
        self.assertEqual(len(default_tasks), 1)
        self.assertEqual(default_tasks[0]["id"], t_active.id)

        # Verify GET /tasks?include_archived=true returns both active and archived tasks
        all_tasks = self.client.get("/tasks?include_archived=true").json()
        self.assertEqual(len(all_tasks), 3)


if __name__ == "__main__":
    unittest.main()

