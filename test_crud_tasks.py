import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.database.models import Base, Horizon2, Ambition, Task
from src.database.crud import create_h2, create_ambition, create_task, get_tasks_by_ambition

# In-memory database for testing
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

def test():
    db = SessionLocal()
    try:
        # Create a role
        role = create_h2(db, name="Work")
        
        # Create an ambition
        ambition = create_ambition(db, outcome="Project X", h2_id=role.id)
        
        # Create tasks
        t1 = create_task(db, title="Task 1", ambition_id=ambition.id)
        t2 = create_task(db, title="Task 2", ambition_id=ambition.id)
        
        # Create a task for another ambition
        ambition2 = create_ambition(db, outcome="Project Y", h2_id=role.id)
        t3 = create_task(db, title="Task 3", ambition_id=ambition2.id)
        
        # Test retrieval
        tasks = get_tasks_by_ambition(db, ambition.id)
        print(f"Ambition 1 ID: {ambition.id}")
        print(f"Tasks for Ambition 1: {[t.title for t in tasks]}")
        assert len(tasks) == 2
        assert "Task 1" in [t.title for t in tasks]
        assert "Task 2" in [t.title for t in tasks]
        
        tasks2 = get_tasks_by_ambition(db, ambition2.id)
        print(f"Ambition 2 ID: {ambition2.id}")
        print(f"Tasks for Ambition 2: {[t.title for t in tasks2]}")
        assert len(tasks2) == 1
        assert "Task 3" in [t.title for t in tasks2]
        
        print("CRUD Test Passed!")
    finally:
        db.close()

if __name__ == "__main__":
    test()
