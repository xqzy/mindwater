import unittest
from unittest.mock import MagicMock, patch
from src.services.email_poller import poll_email_inbox

class TestEmailPoller(unittest.TestCase):
    @patch('src.services.email_poller.imaplib.IMAP4_SSL')
    def test_poll_emails(self, mock_imap):
        # Setup mock
        instance = mock_imap.return_value
        instance.login.return_value = ('OK', [b'Logged in'])
        instance.select.return_value = ('OK', [b'1'])
        instance.search.return_value = ('OK', [b'1'])
        
        # Mock fetch response (RFC822 format)
        msg_data = b'Subject: Test Capture\n\nTake out the trash @home'
        instance.fetch.return_value = ('OK', [(b'1', msg_data)])
        instance.store.return_value = ('OK', [b'1'])
        
        db_mock = MagicMock()
        items = poll_email_inbox(db_mock, "user", "pass", "imap.gmail.com")
        
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].raw_text, "Subject: Test Capture - Take out the trash @home")

if __name__ == '__main__':
    unittest.main()
