import unittest
from src.main_component import DevelopmentArea
from src.models.gtd import Role, Task
from datetime import datetime

class TestMainComponent(unittest.TestCase):
    def test_development_area(self):
        area = DevelopmentArea()
        role = Role(name="Developer", description="Code stuff", icon="💻", priority=1)
        area.set_active_role(role)
        self.assertEqual(area.active_role.name, "Developer")
        
        task = Task(title="Code GTD", estimated_time=30, due_date=datetime.now(), status="todo")
        area.add_task_to_area(task)
        self.assertEqual(len(area.active_tasks), 1)
        self.assertEqual(area.active_tasks[0].title, "Code GTD")

if __name__ == '__main__':
    unittest.main()
