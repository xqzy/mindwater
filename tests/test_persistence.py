import unittest
import os
from src.database.session import SessionLocal, init_db, engine
from src.database.models import Base
from src.database import crud

class TestDatabasePersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a physical file for persistence testing
        if os.path.exists("test_gtd.db"):
            os.remove("test_gtd.db")
        cls.db_url = "sqlite:///test_gtd.db"
        from sqlalchemy import create_engine
        cls.test_engine = create_engine(cls.db_url)
        Base.metadata.create_all(bind=cls.test_engine)
        from sqlalchemy.orm import sessionmaker
        cls.TestSession = sessionmaker(bind=cls.test_engine)

    def setUp(self):
        self.db = self.TestSession()

    def tearDown(self):
        self.db.close()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists("test_gtd.db"):
            os.remove("test_gtd.db")

    def test_full_lifecycle_persistence(self):
        # 1. Create hierarchy
        h5 = crud.create_h5(self.db, name="Purpose", description="Why I do what I do")
        h4 = crud.create_h4(self.db, name="Vision", description="3-5 years", h5_id=h5.id)
        h2 = crud.create_h2(self.db, name="Developer", description="Life Area", h4_id=h4.id)
        ambition = crud.create_ambition(self.db, outcome="GTD App v2", h2_id=h2.id, h4_id=h4.id, h5_id=h5.id)
        task = crud.create_task(self.db, title="Code Models", ambition_id=ambition.id)
        
        # 2. Re-open session and verify
        self.db.close()
        new_db = self.TestSession()
        
        from src.database.models import Task, Horizon2, Ambition
        saved_task = new_db.query(Task).filter_by(title="Code Models").first()
        self.assertIsNotNone(saved_task)
        self.assertEqual(saved_task.ambition.outcome, "GTD App v2")
        self.assertEqual(saved_task.ambition.role.name, "Developer")
        self.assertEqual(saved_task.ambition.vision.name, "Vision")
        self.assertEqual(saved_task.ambition.purpose.name, "Purpose")
        
        new_db.close()

if __name__ == '__main__':
    unittest.main()
