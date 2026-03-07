import unittest
from src.models.gtd import Horizon5, Horizon4, Horizon2, Ambition, Task
from datetime import datetime

class TestGTDIntegrationV2(unittest.TestCase):
    def test_full_hierarchy(self):
        # H5: Purpose
        h5 = Horizon5(name="Purpose", description="Why I do what I do")
        
        # H4: Vision
        h4 = Horizon4(name="Vision", description="3-5 years", h5_id="h5_1")
        
        # H2: Role
        h2 = Horizon2(name="Developer", description="Life Area", h4_id="h4_1")
        
        # H1: Ambition (Project)
        ambition = Ambition(outcome="GTD App v2", status="active", h2_id="h2_1", h4_id="h4_1", h5_id="h5_1")
        h2.ambitions.append(ambition)
        
        # H0: Task (Next Action)
        task = Task(title="Code Models", status="todo", ambition_id="h1_1")
        ambition.tasks.append(task)
        h2.tasks.append(task)
        
        self.assertEqual(len(h2.ambitions), 1)
        self.assertEqual(len(h2.tasks), 1)
        self.assertEqual(h2.ambitions[0].outcome, "GTD App v2")
        self.assertEqual(h2.tasks[0].title, "Code Models")
        self.assertFalse(h2.is_empty)

    def test_empty_role_flagging(self):
        # Role with no ambitions or tasks
        h2_empty = Horizon2(name="Athlete", description="Physical fitness")
        self.assertTrue(h2_empty.is_empty)
        
        # Role with only completed tasks and completed ambitions
        h2_not_active = Horizon2(name="Student")
        h2_not_active.ambitions.append(Ambition(outcome="Graduate", status="completed"))
        h2_not_active.tasks.append(Task(title="Submit Thesis", status="done"))
        self.assertTrue(h2_not_active.is_empty)

        # Role with an active task
        h2_active = Horizon2(name="Parent")
        h2_active.tasks.append(Task(title="Buy milk", status="todo"))
        self.assertFalse(h2_active.is_empty)

if __name__ == '__main__':
    unittest.main()
