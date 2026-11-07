import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.database.models import Base, Horizon2, Ambition
from src.database.session import get_db


class TestProjectPrioritization(unittest.TestCase):
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
        self.role1 = Horizon2(name="Developer", description="Coding")
        self.role2 = Horizon2(name="Athlete", description="Health")
        db.add_all([self.role1, self.role2])
        db.commit()
        db.refresh(self.role1)
        db.refresh(self.role2)
        self.role1_id = self.role1.id
        self.role2_id = self.role2.id
        db.close()

    def tearDown(self):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_sequential_default_priority_and_explicit_insertion(self):
        r1 = self.client.post("/ambitions", json={"outcome": "Project Alpha", "h2_id": self.role1_id})
        r2 = self.client.post("/ambitions", json={"outcome": "Project Beta", "h2_id": self.role1_id})
        r3 = self.client.post("/ambitions", json={"outcome": "Project Gamma", "h2_id": self.role2_id})
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r3.status_code, 200)

        projects = self.client.get("/ambitions").json()
        self.assertEqual(
            [(p["outcome"], p["priority"]) for p in projects],
            [("Project Alpha", 1), ("Project Beta", 2), ("Project Gamma", 3)],
        )

        # Insert a new project explicitly at priority #1
        r4 = self.client.post(
            "/ambitions",
            json={"outcome": "Urgent Launch", "h2_id": self.role1_id, "priority": 1},
        )
        self.assertEqual(r4.status_code, 200)

        projects = self.client.get("/ambitions").json()
        self.assertEqual(
            [(p["outcome"], p["priority"]) for p in projects],
            [
                ("Urgent Launch", 1),
                ("Project Alpha", 2),
                ("Project Beta", 3),
                ("Project Gamma", 4),
            ],
        )

    def test_update_project_priority_number_shifts_others(self):
        p1 = self.client.post("/ambitions", json={"outcome": "P1", "h2_id": self.role1_id}).json()
        p2 = self.client.post("/ambitions", json={"outcome": "P2", "h2_id": self.role1_id}).json()
        p3 = self.client.post("/ambitions", json={"outcome": "P3", "h2_id": self.role2_id}).json()

        # Move P3 from #3 to #1 via priority number update
        res = self.client.put(f"/ambitions/{p3['id']}", json={"priority": 1})
        self.assertEqual(res.status_code, 200)

        projects = self.client.get("/ambitions").json()
        self.assertEqual(
            [(p["outcome"], p["priority"]) for p in projects],
            [("P3", 1), ("P1", 2), ("P2", 3)],
        )

        # Move P3 from #1 to #2
        res2 = self.client.put(f"/ambitions/{p3['id']}", json={"priority": 2})
        self.assertEqual(res2.status_code, 200)

        projects = self.client.get("/ambitions").json()
        self.assertEqual(
            [(p["outcome"], p["priority"]) for p in projects],
            [("P1", 1), ("P3", 2), ("P2", 3)],
        )

    def test_drag_and_drop_reorder_full_and_role_filtered(self):
        p1 = self.client.post("/ambitions", json={"outcome": "Dev 1", "h2_id": self.role1_id}).json()
        p2 = self.client.post("/ambitions", json={"outcome": "Sport 1", "h2_id": self.role2_id}).json()
        p3 = self.client.post("/ambitions", json={"outcome": "Dev 2", "h2_id": self.role1_id}).json()
        p4 = self.client.post("/ambitions", json={"outcome": "Sport 2", "h2_id": self.role2_id}).json()

        # Full reorder: [p4, p1, p3, p2]
        res = self.client.post(
            "/ambitions/reorder",
            json={"ordered_ids": [p4["id"], p1["id"], p3["id"], p2["id"]]},
        )
        self.assertEqual(res.status_code, 200)

        projects = self.client.get("/ambitions").json()
        self.assertEqual(
            [(p["outcome"], p["priority"]) for p in projects],
            [("Sport 2", 1), ("Dev 1", 2), ("Dev 2", 3), ("Sport 1", 4)],
        )

        # Role-filtered reorder: swap only Developer projects (Dev 1 at slot #2, Dev 2 at slot #3 -> [Dev 2, Dev 1])
        res_subset = self.client.post(
            "/ambitions/reorder",
            json={"ordered_ids": [p3["id"], p1["id"]]},
        )
        self.assertEqual(res_subset.status_code, 200)

        projects = self.client.get("/ambitions").json()
        self.assertEqual(
            [(p["outcome"], p["priority"]) for p in projects],
            [("Sport 2", 1), ("Dev 2", 2), ("Dev 1", 3), ("Sport 1", 4)],
        )


if __name__ == "__main__":
    unittest.main()
