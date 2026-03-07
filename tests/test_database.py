import unittest
from src.database.session import SessionLocal, init_db, engine
from src.database.models import Base
from src.database import crud

class TestDatabaseCRUD(unittest.TestCase):
    def setUp(self):
        # Create a clean in-memory database for testing
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=engine)

    def test_create_h5_purpose(self):
        h5 = crud.create_h5(self.db, name="Life Mission", description="To help others", icon="🌟")
        self.assertEqual(h5.name, "Life Mission")
        self.assertEqual(h5.description, "To help others")

    def test_create_h4_vision(self):
        h5 = crud.create_h5(self.db, name="Life Mission")
        h4 = crud.create_h4(self.db, name="Career Mastery", h5_id=h5.id)
        self.assertEqual(h4.name, "Career Mastery")
        self.assertEqual(h4.h5_id, h5.id)

    def test_create_h2_role(self):
        h2 = crud.create_h2(self.db, name="Developer", description="Maintain systems and code")
        self.assertEqual(h2.name, "Developer")

    def test_create_ambition_and_task(self):
        role = crud.create_h2(self.db, name="Developer")
        ambition = crud.create_ambition(self.db, outcome="Complete GTD App", h2_id=role.id)
        task = crud.create_task(self.db, title="Design Schema", ambition_id=ambition.id, context_tags=["@computer"])
        
        self.assertEqual(ambition.h2_id, role.id)
        self.assertEqual(task.ambition_id, ambition.id)
        self.assertIn("@computer", task.context_tags)

    def test_filtered_listing(self):
        t1 = crud.create_task(self.db, title="Low energy task", energy_level="Low", context_tags=["@home"])
        t2 = crud.create_task(self.db, title="High energy task", energy_level="High", context_tags=["@computer"])
        
        low_energy = crud.filter_tasks(self.db, energy_level="Low")
        computer_tasks = crud.filter_tasks(self.db, context_tag="@computer")
        
        self.assertEqual(len(low_energy), 1)
        self.assertEqual(low_energy[0].title, "Low energy task")
        self.assertEqual(len(computer_tasks), 1)
        self.assertEqual(computer_tasks[0].title, "High energy task")

    def test_empty_role_check(self):
        role_empty = crud.create_h2(self.db, name="Empty Role")
        role_active = crud.create_h2(self.db, name="Active Role")
        crud.create_task(self.db, title="Task", role_id=role_active.id)
        
        empty_roles = crud.get_empty_roles(self.db)
        self.assertEqual(len(empty_roles), 1)
        self.assertEqual(empty_roles[0].name, "Empty Role")

if __name__ == '__main__':
    unittest.main()
