import unittest
from fastapi.testclient import TestClient
from src.api.main import app
from src.database.session import SessionLocal, Base, engine
from src.database.models import Inbox

class TestCaptureIntegration(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=engine)

    def test_end_to_end_api_capture(self):
        # 1. Post to API
        response = self.client.post("/capture", json={"text": "Buy groceries @store #errand"})
        self.assertEqual(response.status_code, 200)
        
        # 2. Check Database
        item = self.db.query(Inbox).first()
        self.assertIsNotNone(item)
        self.assertEqual(item.raw_text, "Buy groceries @store #errand")
        self.assertEqual(item.source_tag, "api")

if __name__ == '__main__':
    unittest.main()
