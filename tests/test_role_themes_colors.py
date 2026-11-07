import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.database.models import Base
from src.database.session import get_db


class TestRoleThemesAndColors(unittest.TestCase):
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

    def tearDown(self):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_role_color_and_theme_inherited_by_projects(self):
        # Create a Role with a cartoon/Disney theme and color
        r_res = self.client.post(
            "/roles",
            json={
                "name": "Creative Director",
                "description": "Animation & Design",
                "color": "#d97706",
                "theme_key": "lion_king",
            },
        )
        self.assertEqual(r_res.status_code, 200)
        role_data = r_res.json()
        role_id = role_data["id"]

        roles = self.client.get("/roles").json()
        self.assertEqual(len(roles), 1)
        self.assertEqual(roles[0]["color"], "#d97706")
        self.assertEqual(roles[0]["theme_key"], "lion_king")

        # Create a Project under this Role and verify it inherits role_color & role_theme_key
        p_res = self.client.post(
            "/ambitions",
            json={"outcome": "Launch Storyboard", "h2_id": role_id},
        )
        self.assertEqual(p_res.status_code, 200)

        projects = self.client.get("/ambitions").json()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["role_color"], "#d97706")
        self.assertEqual(projects[0]["role_theme_key"], "lion_king")

        # Update the Role's theme & color and verify the Project reflects the new color coding
        u_res = self.client.put(
            f"/roles/{role_id}",
            json={
                "name": "Creative Director",
                "description": "Animation & Design",
                "color": "#7c3aed",
                "theme_key": "aladdin",
            },
        )
        self.assertEqual(u_res.status_code, 200)

        projects_after = self.client.get("/ambitions").json()
        self.assertEqual(projects_after[0]["role_color"], "#7c3aed")
        self.assertEqual(projects_after[0]["role_theme_key"], "aladdin")


if __name__ == "__main__":
    unittest.main()

