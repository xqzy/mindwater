import unittest
from src.models.gtd import Horizon5, Horizon4, Horizon2, Ambition, Task, Inbox
from datetime import datetime

class TestGTDModelsV2(unittest.TestCase):
    def test_create_h5_purpose(self):
        h5 = Horizon5(name="Life Mission", description="To help others", icon="🌟")
        self.assertEqual(h5.name, "Life Mission")
        self.assertEqual(h5.description, "To help others")

    def test_create_h4_vision(self):
        h4 = Horizon4(name="Career Mastery", description="Become a lead dev in 3 years", target_date="2029-01-01")
        self.assertEqual(h4.name, "Career Mastery")

    def test_create_h2_role(self):
        h2 = Horizon2(name="Developer", description="Maintain systems and code")
        self.assertEqual(h2.name, "Developer")

    def test_create_ambition_v2(self):
        ambition = Ambition(outcome="Complete GTD App", status="active", h2_id="h2_1")
        self.assertEqual(ambition.outcome, "Complete GTD App")
        self.assertEqual(ambition.status, "active")

    def test_create_task_v2(self):
        task = Task(title="Design V2 Schema", context_tags=["@computer"], energy_level="High", status="todo")
        self.assertEqual(task.title, "Design V2 Schema")
        self.assertIn("@computer", task.context_tags)
        self.assertEqual(task.energy_level, "High")

    def test_create_inbox(self):
        inbox = Inbox(raw_text="Call mom", source_tag="voice")
        self.assertEqual(inbox.raw_text, "Call mom")
        self.assertEqual(inbox.source_tag, "voice")
        self.assertIsInstance(inbox.timestamp, datetime)

if __name__ == '__main__':
    unittest.main()
