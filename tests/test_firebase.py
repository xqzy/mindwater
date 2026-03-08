import unittest
from unittest.mock import patch, MagicMock
from src.database.firebase import add_to_inbox, get_db

class TestFirebaseIntegration(unittest.TestCase):

    @patch('src.database.firebase.firestore')
    @patch('src.database.firebase.firebase_admin')
    def test_add_to_inbox(self, mock_firebase_admin, mock_firestore):
        # Setup mock db
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_document = MagicMock()
        mock_document.id = "mock_doc_id"
        
        mock_firestore.client.return_value = mock_db
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document

        # Reset the global db instance for test
        import src.database.firebase as fb
        fb._db = None

        raw_text = "Test task #test @home"
        parsed_data = {
            "text": "Test task",
            "tags": ["#test"],
            "contexts": ["@home"]
        }
        
        doc_id = add_to_inbox(raw_text, parsed_data)
        
        self.assertEqual(doc_id, "mock_doc_id")
        mock_db.collection.assert_called_once_with("inbox")
        mock_collection.document.assert_called_once()
        mock_document.set.assert_called_once()
        
        called_args = mock_document.set.call_args[0][0]
        self.assertEqual(called_args["raw_text"], raw_text)
        self.assertEqual(called_args["clean_text"], "Test task")
        self.assertEqual(called_args["tags"], ["#test"])
        self.assertEqual(called_args["contexts"], ["@home"])
        self.assertEqual(called_args["source"], "tui")
        self.assertIn("timestamp", called_args)

if __name__ == '__main__':
    unittest.main()
