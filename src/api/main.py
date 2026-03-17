import os
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database.session import get_db, init_db
from src.database import crud
from src.services.parser import parse_capture_text

app = FastAPI()

# Get the path to the static directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Create static directory if it doesn't exist
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

@app.get("/")
def read_root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "Mindwater API is running", "environment": "production", "message": "index.html not found"}

class CaptureRequest(BaseModel):
    text: str
    source: str = "api"

class ClarifyRequest(BaseModel):
    type: str # "task" or "ambition"
    title: str
    role_id: Optional[int] = None
    ambition_id: Optional[int] = None
    energy_level: Optional[str] = "Medium"
    estimated_time: Optional[int] = 0
    context_tags: Optional[List[str]] = []

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    return crud.get_all_roles(db)

@app.get("/ambitions")
def get_ambitions(db: Session = Depends(get_db)):
    return crud.get_ambitions_with_task_counts(db)

@app.post("/capture")
def capture_item(request: CaptureRequest, db: Session = Depends(get_db)):
    # Parse the text (for future structured use)
    parsed = parse_capture_text(request.text)
    
    # Save to Inbox table
    inbox_item = crud.create_inbox_item(db, raw_text=request.text, source_tag=request.source)
    
    return {
        "status": "success",
        "item": {
            "id": inbox_item.id,
            "raw_text": inbox_item.raw_text,
            "source": inbox_item.source_tag,
            "timestamp": inbox_item.timestamp
        }
    }

@app.get("/inbox")
def get_inbox(limit: int = 50, db: Session = Depends(get_db)):
    items = crud.get_inbox_items(db, limit=limit)
    return items

@app.delete("/inbox/{item_id}")
def delete_inbox_item(item_id: int, db: Session = Depends(get_db)):
    success = crud.delete_inbox_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success"}

@app.post("/inbox/{item_id}/clarify")
def clarify_inbox_item(item_id: int, request: ClarifyRequest, db: Session = Depends(get_db)):
    # 1. Verify inbox item exists
    inbox_item = db.query(crud.models.Inbox).filter(crud.models.Inbox.id == item_id).first()
    if not inbox_item:
        raise HTTPException(status_code=404, detail="Inbox item not found")

    # 2. Create the target record
    if request.type == "task":
        crud.create_task(
            db,
            title=request.title,
            ambition_id=request.ambition_id,
            role_id=request.role_id,
            energy_level=request.energy_level,
            estimated_time=request.estimated_time,
            context_tags=request.context_tags
        )
    elif request.type == "ambition":
        crud.create_ambition(
            db,
            outcome=request.title,
            h2_id=request.role_id
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid clarification type")

    # 3. Delete from inbox
    crud.delete_inbox_item(db, item_id)
    
    return {"status": "success"}

# Mount the static directory at /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
