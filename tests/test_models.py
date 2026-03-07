import unittest
from src.models.gtd import Role, Ambition, Task
from datetime import datetime

class TestGTDModels(unittest.TestCase):
    def test_create_role(self):
        role = Role(name="Professional", description="Work related tasks", icon="💼", priority=1)
        self.assertEqual(role.name, "Professional")
        self.assertEqual(role.description, "Work related tasks")
        self.assertEqual(role.icon, "💼")
        self.assertEqual(role.priority, 1)

    def test_create_ambition(self):
        ambition = Ambition(outcome="Complete Project", target_date=datetime(2026, 12, 31), status="active")
        self.assertEqual(ambition.outcome, "Complete Project")
        self.assertEqual(ambition.status, "active")

    def test_create_task(self):
        task = Task(title="Design Schema", estimated_time=60, due_date=datetime(2026, 3, 10), status="todo")
        self.assertEqual(task.title, "Design Schema")
        self.assertEqual(task.status, "todo")

if __name__ == '__main__':
    unittest.main()
