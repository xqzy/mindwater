import os
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Initialize Firebase App
_db = None

def get_db():
    global _db
    if _db is not None:
        return _db
    
    # Try to initialize firebase-admin
    # It will automatically pick up GOOGLE_APPLICATION_CREDENTIALS if set,
    # or you can explicitly provide a path via FIREBASE_CREDENTIALS
    cred_path = os.environ.get("FIREBASE_CREDENTIALS")
    try:
        if not firebase_admin._apps:
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Fall back to default credentials
                firebase_admin.initialize_app()
        _db = firestore.client()
        return _db
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Firebase: {e}")

def add_to_inbox(raw_text: str, parsed_data: dict):
    """
    Saves captured item to Firebase Firestore 'inbox' collection.
    """
    try:
        db = get_db()
    except RuntimeError as e:
        # Re-raise or handle if required
        raise e

    doc_ref = db.collection("inbox").document()
    doc_ref.set({
        "raw_text": raw_text,
        "clean_text": parsed_data.get("text", ""),
        "tags": parsed_data.get("tags", []),
        "contexts": parsed_data.get("contexts", []),
        "source": "tui",
        "timestamp": datetime.datetime.now(datetime.timezone.utc)
    })
    return doc_ref.id
