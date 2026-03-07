import unittest
from src.services.parser import parse_capture_text

class TestParser(unittest.TestCase):
    def test_parse_tags_and_contexts(self):
        text = "Call mom @calls #family"
        result = parse_capture_text(text)
        self.assertEqual(result['text'], "Call mom")
        self.assertIn("@calls", result['contexts'])
        self.assertIn("#family", result['tags'])

    def test_strip_email_signature(self):
        text = "Meeting at 5pm\n--\nBest regards,\nRob"
        result = parse_capture_text(text)
        self.assertEqual(result['text'], "Meeting at 5pm")

    def test_raw_text_on_no_metadata(self):
        text = "Just a simple thought"
        result = parse_capture_text(text)
        self.assertEqual(result['text'], "Just a simple thought")
        self.assertEqual(result['tags'], [])
        self.assertEqual(result['contexts'], [])

if __name__ == '__main__':
    unittest.main()
