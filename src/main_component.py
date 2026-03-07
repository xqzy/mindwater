# main_component.py
# This serves as the primary development area component for the GTD app logic.

class DevelopmentArea:
    def __init__(self):
        self.active_role = None
        self.active_ambition = None
        self.active_tasks = []

    def set_active_role(self, role):
        self.active_role = role
        print(f"Active Role set to: {role.name}")

    def add_task_to_area(self, task):
        self.active_tasks.append(task)
        print(f"Task added to development area: {task.title}")
