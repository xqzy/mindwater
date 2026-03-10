
import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Task, Ambition, Horizon2
from src.database import crud

class TestHorizonRefinement(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_get_ambitions_by_role(self):
        r1 = crud.create_h2(self.db, name="Work")
        r2 = crud.create_h2(self.db, name="Personal")
        
        crud.create_ambition(self.db, outcome="Project 1", h2_id=r1.id)
        crud.create_ambition(self.db, outcome="Project 2", h2_id=r1.id)
        crud.create_ambition(self.db, outcome="Project 3", h2_id=r2.id)
        
        work_projects = crud.get_ambitions_by_role(self.db, r1.id)
        self.assertEqual(len(work_projects), 2)
        
        personal_projects = crud.get_ambitions_by_role(self.db, r2.id)
        self.assertEqual(len(personal_projects), 1)

    def test_update_role_and_ambition(self):
        role = crud.create_h2(self.db, name="Old Name", description="Old Desc")
        crud.update_role(self.db, role.id, name="New Name", description="New Desc")
        
        updated_role = crud.get_role(self.db, role.id)
        self.assertEqual(updated_role.name, "New Name")
        self.assertEqual(updated_role.description, "New Desc")
        
        ambition = crud.create_ambition(self.db, outcome="Old Outcome")
        crud.update_ambition(self.db, ambition.id, outcome="New Outcome", status="done")
        
        updated_ambition = crud.get_ambition(self.db, ambition.id)
        self.assertEqual(updated_ambition.outcome, "New Outcome")
        self.assertEqual(updated_ambition.status, "done")

    def test_ambition_stats(self):
        role = crud.create_h2(self.db, name="Work")
        ambition = crud.create_ambition(self.db, outcome="Project", h2_id=role.id)
        
        # 1 task finished today (within 2 weeks and 6 weeks)
        t1 = crud.create_task(self.db, title="T1", ambition_id=ambition.id, estimated_time=60)
        crud.update_task_status(self.db, t1.id, "done")
        
        # 1 task finished 3 weeks ago (within 6 weeks, not 2 weeks)
        t2 = crud.create_task(self.db, title="T2", ambition_id=ambition.id, estimated_time=30)
        crud.update_task_status(self.db, t2.id, "done")
        # Manually override completed_at for testing
        t2_db = self.db.query(Task).filter(Task.id == t2.id).first()
        t2_db.completed_at = datetime.now() - timedelta(days=21)
        self.db.commit()
        
        # 1 task finished 8 weeks ago (neither)
        t3 = crud.create_task(self.db, title="T3", ambition_id=ambition.id, estimated_time=120)
        crud.update_task_status(self.db, t3.id, "done")
        t3_db = self.db.query(Task).filter(Task.id == t3.id).first()
        t3_db.completed_at = datetime.now() - timedelta(days=60)
        self.db.commit()
        
        # 1 task not finished
        t4 = crud.create_task(self.db, title="T4", ambition_id=ambition.id, estimated_time=100)
        
        stats = crud.get_ambition_stats(self.db, ambition.id)
        
        self.assertEqual(stats["total_hours"], 3.5) # 60 + 30 + 120 = 210 mins = 3.5 hours
        self.assertEqual(stats["finished_2w"], 1)
        self.assertEqual(stats["finished_6w"], 2)
        self.assertEqual(stats["total_finished"], 3)

if __name__ == '__main__':
    unittest.main()
