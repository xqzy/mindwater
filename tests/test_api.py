import unittest
from fastapi.testclient import TestClient
from src.api.main import app
from src.database.session import SessionLocal, Base, engine

class TestCaptureAPI(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def test_capture_endpoint(self):
        response = self.client.post("/capture", json={"text": "Buy groceries @store #errand"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["item"]["raw_text"], "Buy groceries @store #errand")

if __name__ == '__main__':
    unittest.main()
