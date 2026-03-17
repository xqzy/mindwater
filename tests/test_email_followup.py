import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.database import crud
from src.services.email_poller import get_flagged_emails

class TestEmailFollowup(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for testing
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    @patch('src.services.email_poller.imaplib.IMAP4_SSL')
    def test_get_flagged_emails(self, mock_imap):
        # Mock IMAP connection
        instance = mock_imap.return_request.return_value # Wait, return_value is the instance
        instance = mock_imap.return_value
        instance.login.return_value = ('OK', [b'Logged in'])
        instance.select.return_value = ('OK', [b'1'])
        
        # Mock search result (one email)
        instance.search.return_value = ('OK', [b'1'])
        
        # Mock fetch result (header fields)
        header_data = b'Subject: Follow-up test\r\nFrom: sender@example.com\r\nDate: Thu, 12 Mar 2026 10:00:00 +0000\r\nMessage-ID: <test-id-123>\r\n\r\n'
        instance.fetch.return_value = ('OK', [(b'1 (BODY[HEADER.FIELDS (SUBJECT FROM DATE MESSAGE-ID)] {120}', header_data), b')'])
        
        emails = get_flagged_emails(self.db, "user", "pass", "host")
        
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]['subject'], "Follow-up test")
        self.assertEqual(emails[0]['id'], "<test-id-123>")

    @patch('src.services.email_poller.imaplib.IMAP4_SSL')
    def test_dismiss_email(self, mock_imap):
        # Mock IMAP
        instance = mock_imap.return_value
        instance.login.return_value = ('OK', [b'Logged in'])
        instance.select.return_value = ('OK', [b'1'])
        instance.search.return_value = ('OK', [b'1'])
        header_data = b'Subject: Test\r\nFrom: me\r\nDate: now\r\nMessage-ID: <id-1>\r\n\r\n'
        instance.fetch.return_value = ('OK', [(b'1', header_data), b')'])
        
        # Initially 1 email
        emails = get_flagged_emails(self.db, "user", "pass", "host")
        self.assertEqual(len(emails), 1)
        
        # Dismiss it
        crud.create_dismissed_email(self.db, "<id-1>")
        
        # Now 0 emails
        emails = get_flagged_emails(self.db, "user", "pass", "host")
        self.assertEqual(len(emails), 0)

if __name__ == '__main__':
    unittest.main()
