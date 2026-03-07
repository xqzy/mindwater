import unittest
from src.models.gtd import Role, Ambition, Task
from datetime import datetime

class TestGTDIntegration(unittest.TestCase):
    def test_flexible_mapping(self):
        # Create a Role
        role = Role(name="Work", description="Work stuff", icon="💼", priority=1)
        
        # Create an Ambition linked to Role
        ambition = Ambition(outcome="Ship Product", target_date=datetime(2026, 6, 1), status="active", role_id=1)
        role.ambitions.append(ambition)
        
        # Create a Task linked to Ambition
        task1 = Task(title="Write Code", estimated_time=120, due_date=datetime(2026, 3, 15), status="todo", ambition_id=1)
        ambition.tasks.append(task1)
        
        # Create a Task linked directly to Role
        task2 = Task(title="Check Email", estimated_time=15, due_date=datetime(2026, 3, 8), status="todo", role_id=1)
        role.tasks.append(task2)
        
        self.assertEqual(len(role.ambitions), 1)
        self.assertEqual(len(role.tasks), 1)
        self.assertEqual(len(ambition.tasks), 1)
        self.assertEqual(role.ambitions[0].outcome, "Ship Product")
        self.assertEqual(role.tasks[0].title, "Check Email")
        self.assertEqual(ambition.tasks[0].title, "Write Code")

if __name__ == '__main__':
    unittest.main()
