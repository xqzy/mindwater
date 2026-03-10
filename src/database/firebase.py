import os
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv

load_dotenv()

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
    
    # If not in env, search for mindwater-*.json in root
    if not cred_path:
        import glob
        matches = glob.glob("mindwater-*.json")
        if matches:
            # Sort to be deterministic if multiple files exist
            matches.sort()
            cred_path = matches[0]

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
        raise RuntimeError(f"Failed to initialize Firebase with {cred_path if cred_path else 'default credentials'}: {e}")

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

def get_inbox_items():
    """
    Retrieves all items from the 'inbox' collection, sorted by timestamp descending.
    """
    try:
        db = get_db()
    except RuntimeError as e:
        raise e
        
    docs = db.collection("inbox").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    items = []
    for doc in docs:
        item_data = doc.to_dict()
        item_data["id"] = doc.id
        items.append(item_data)
    return items

def delete_inbox_item(doc_id: str):
    """
    Deletes an item from the 'inbox' collection by its document ID.
    """
    try:
        db = get_db()
        db.collection("inbox").document(doc_id).delete()
    except Exception as e:
        raise RuntimeError(f"Failed to delete inbox item {doc_id}: {e}")

