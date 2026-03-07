import unittest
from unittest.mock import patch, MagicMock
from src.cli.capture import main

class TestCLI(unittest.TestCase):
    @patch('src.cli.capture.requests.post')
    def test_cli_capture(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}
        
        # Simulate running 'python capture.py "Test task"'
        with patch('sys.argv', ['capture.py', 'Test task']):
            main()
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs['json']['text'], 'Test task')

if __name__ == '__main__':
    unittest.main()
