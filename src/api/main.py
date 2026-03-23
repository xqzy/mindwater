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
from src.services.email_poller import get_flagged_emails
from src.services.todoist import push_task_to_todoist

app = FastAPI()

# Get the path to the static directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Create static directory if it doesn't exist
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# --- Pydantic Models ---

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
    email_id: Optional[str] = None # For clarifying emails

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    energy_level: Optional[str] = None
    estimated_time: Optional[int] = None
    role_id: Optional[int] = None
    ambition_id: Optional[int] = None
    context_tags: Optional[List[str]] = None
    planned_date: Optional[datetime] = None

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None

class AmbitionCreate(BaseModel):
    outcome: str
    h2_id: Optional[int] = None
    status: Optional[str] = "active"

# --- Endpoints ---

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "Mindwater API is running", "environment": "production", "message": "index.html not found"}

@app.get("/config")
def get_config():
    return {
        "todoist_enabled": bool(os.getenv("TODOIST_API_TOKEN") or os.getenv("FIREBASE_CREDENTIALS")),
        "email_enabled": bool(os.getenv("EMAIL_USER") and os.getenv("EMAIL_PASSWORD"))
    }

# --- Inbox & Capture ---

@app.post("/capture")
def capture_item(request: CaptureRequest, db: Session = Depends(get_db)):
    # Save to Inbox table
    inbox_item = crud.create_inbox_item(db, raw_text=request.text, source_tag=request.source)
    return {"status": "success", "id": inbox_item.id}

@app.get("/inbox")
def get_inbox(limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_inbox_items(db, limit=limit)

@app.delete("/inbox/{item_id}")
def delete_inbox_item(item_id: int, db: Session = Depends(get_db)):
    success = crud.delete_inbox_item(db, item_id)
    if not success: raise HTTPException(status_code=404)
    return {"status": "success"}

@app.post("/inbox/{item_id}/clarify")
def clarify_inbox_item(item_id: int, request: ClarifyRequest, db: Session = Depends(get_db)):
    # Verify inbox item exists (skip check if it's an email clarify or a direct add with id=0)
    if not request.email_id and item_id > 0:
        inbox_item = db.query(crud.models.Inbox).filter(crud.models.Inbox.id == item_id).first()
        if not inbox_item: raise HTTPException(status_code=404, detail="Inbox item not found")

    # Create target record
    if request.type == "task":
        crud.create_task(db, title=request.title, ambition_id=request.ambition_id, 
                        role_id=request.role_id, energy_level=request.energy_level, 
                        estimated_time=request.estimated_time, context_tags=request.context_tags)
    elif request.type == "ambition":
        crud.create_ambition(db, outcome=request.title, h2_id=request.role_id)
    
    # Cleanup
    if request.email_id:
        crud.create_dismissed_email(db, request.email_id)
    elif item_id > 0:
        crud.delete_inbox_item(db, item_id)
    
    return {"status": "success"}

# --- Emails ---

@app.get("/emails/flagged")
def get_emails(db: Session = Depends(get_db)):
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    host = os.getenv("EMAIL_IMAP_HOST")
    if not all([user, password, host]):
        return []
    return get_flagged_emails(db, user, password, host)

@app.post("/emails/dismiss/{email_id}")
def dismiss_email(email_id: str, db: Session = Depends(get_db)):
    crud.create_dismissed_email(db, email_id)
    return {"status": "success"}

# --- Tasks ---

@app.get("/tasks")
def get_tasks(role_id: Optional[int] = None, context: Optional[str] = None, energy: Optional[str] = None, db: Session = Depends(get_db)):
    tasks = crud.get_filtered_tasks(db, role_id=role_id, context_tag=context, energy_level=energy)
    return [{
        "id": t.id,
        "title": t.title,
        "status": t.status,
        "energy_level": t.energy_level,
        "estimated_time": t.estimated_time,
        "context_tags": t.context_tags,
        "role_id": t.role_id,
        "role": {"id": t.role.id, "name": t.role.name} if t.role else None,
        "ambition_id": t.ambition_id,
        "ambition": {"id": t.ambition.id, "outcome": t.ambition.outcome} if t.ambition else None
    } for t in tasks]

@app.patch("/tasks/{task_id}/status")
def toggle_task_status(task_id: int, status: str, db: Session = Depends(get_db)):
    crud.update_task_status(db, task_id, status)
    return {"status": "success"}

@app.put("/tasks/{task_id}")
def update_task_details(task_id: int, update: TaskUpdate, db: Session = Depends(get_db)):
    crud.update_task(db, task_id, **update.dict(exclude_unset=True))
    return {"status": "success"}

@app.post("/tasks/{task_id}/push-todoist")
def push_to_todoist(task_id: int, db: Session = Depends(get_db)):
    task = db.query(crud.models.Task).filter(crud.models.Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404)
    todoist_id = push_task_to_todoist(task.title, task.planned_date)
    return {"status": "success", "todoist_id": todoist_id}

# --- Horizons ---

@app.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    roles = crud.get_all_roles(db)
    return [{"id": r.id, "name": r.name, "description": r.description} for r in roles]

@app.post("/roles")
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    return crud.create_h2(db, name=role.name, description=role.description)

@app.put("/roles/{role_id}")
def update_role(role_id: int, role: RoleCreate, db: Session = Depends(get_db)):
    return crud.update_role(db, role_id, **role.dict())

@app.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    crud.delete_role(db, role_id)
    return {"status": "success"}

@app.get("/ambitions")
def get_ambitions(db: Session = Depends(get_db)):
    # Returning with task counts for the review/projects view
    return crud.get_ambitions_with_task_counts(db)

@app.post("/ambitions")
def create_ambition(ambition: AmbitionCreate, db: Session = Depends(get_db)):
    return crud.create_ambition(db, outcome=ambition.outcome, h2_id=ambition.h2_id)

@app.put("/ambitions/{ambition_id}")
def update_ambition(ambition_id: int, ambition: AmbitionCreate, db: Session = Depends(get_db)):
    return crud.update_ambition(db, ambition_id, **ambition.dict())

@app.delete("/ambitions/{ambition_id}")
def delete_ambition(ambition_id: int, db: Session = Depends(get_db)):
    crud.delete_ambition(db, ambition_id)
    return {"status": "success"}

@app.get("/ambitions/{ambition_id}/stats")
def get_ambition_stats(ambition_id: int, db: Session = Depends(get_db)):
    return crud.get_ambition_stats(db, ambition_id)

@app.get("/ambitions/{ambition_id}/tasks")
def get_ambition_tasks(ambition_id: int, db: Session = Depends(get_db)):
    tasks = crud.get_tasks_by_ambition(db, ambition_id)
    return [{
        "id": t.id,
        "title": t.title,
        "status": t.status,
        "energy_level": t.energy_level,
        "estimated_time": t.estimated_time,
        "actual_time": t.actual_time
    } for t in tasks]

# --- Review ---

@app.get("/review/last")
def get_last_review(db: Session = Depends(get_db)):
    review = crud.get_last_review(db)
    return {"timestamp": review.timestamp if review else None}

@app.post("/review/complete")
def complete_review(db: Session = Depends(get_db)):
    crud.record_review(db)
    return {"status": "success"}

@app.get("/review/roles-summary")
def get_roles_summary(db: Session = Depends(get_db)):
    summary = crud.get_roles_with_ambition_counts(db)
    # Convert Role objects to dicts for JSON serialization
    return [{"role": {"id": r.id, "name": r.name}, "count": count} for r, count in summary]

# Mount the static directory at /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
