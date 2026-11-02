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
from src.services.todoist import (
    get_todoist_token,
    mask_token,
    fetch_todoist_projects,
    create_todoist_project,
    update_todoist_project,
    fetch_todoist_labels,
    create_todoist_label,
    update_todoist_label,
    close_todoist_task,
    reopen_todoist_task,
    delete_todoist_task,
    export_mindwater_task_to_todoist,
    sync_with_todoist,
)

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

class TodoistSettingsRequest(BaseModel):
    token: str

class RoleTodoistMappingRequest(BaseModel):
    role_id: int
    todoist_project_id: Optional[str] = None
    todoist_project_name: Optional[str] = None
    create_new: bool = False

class AmbitionTodoistMappingRequest(BaseModel):
    ambition_id: int
    todoist_label_id: Optional[str] = None
    todoist_label_name: Optional[str] = None
    create_new: bool = False

class BatchPushTodoistRequest(BaseModel):
    task_ids: List[int]

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
def get_config(db: Session = Depends(get_db)):
    token = get_todoist_token(db)
    return {
        "todoist_enabled": bool(token or os.getenv("FIREBASE_CREDENTIALS")),
        "todoist_token_masked": mask_token(token),
        "last_todoist_sync": crud.get_setting(db, "last_todoist_sync"),
        "email_enabled": bool(os.getenv("EMAIL_USER") and os.getenv("EMAIL_PASSWORD"))
    }

# --- Todoist Settings, Sync & Mapping ---

@app.get("/todoist/settings")
def get_todoist_settings(db: Session = Depends(get_db)):
    token = get_todoist_token(db)
    return {
        "configured": bool(token),
        "masked_token": mask_token(token),
        "last_sync": crud.get_setting(db, "last_todoist_sync")
    }

@app.post("/todoist/settings")
def save_todoist_settings(req: TodoistSettingsRequest, db: Session = Depends(get_db)):
    clean_token = req.token.strip()
    if not clean_token:
        raise HTTPException(status_code=400, detail="Please enter a non-empty Todoist API token.")

    # Verify token connectivity with Todoist before saving
    connection_ok = False
    project_count = 0
    connection_error = None
    try:
        projects = fetch_todoist_projects(clean_token)
        connection_ok = True
        project_count = len(projects)
    except Exception as e:
        connection_error = str(e)

    crud.set_setting(db, "todoist_api_token", clean_token)
    return {
        "status": "success" if connection_ok else "warning",
        "configured": True,
        "masked_token": mask_token(clean_token),
        "connection_ok": connection_ok,
        "project_count": project_count,
        "connection_error": connection_error,
        "message": (
            f"Token saved & verified with Todoist ({project_count} project(s) found)."
            if connection_ok
            else f"Token saved locally, but Todoist rejected or failed connection: {connection_error}"
        )
    }

@app.post("/todoist/sync")
def trigger_todoist_sync(db: Session = Depends(get_db)):
    try:
        result = sync_with_todoist(db)
        if result.get("status") == "skipped":
            raise HTTPException(status_code=400, detail=result.get("reason", "Todoist API token is not configured yet. Please save your token in the Todoist tab first."))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Todoist sync failed: {str(e)}")

@app.get("/todoist/mappings")
def get_todoist_mappings(db: Session = Depends(get_db)):
    token = get_todoist_token(db)
    roles = crud.get_all_roles(db)
    ambitions = crud.get_ambitions_with_task_counts(db, status="active")

    remote_projects = []
    remote_labels = []
    remote_error = None
    if token:
        try:
            remote_projects = fetch_todoist_projects(token)
        except Exception as e:
            remote_error = str(e)
        try:
            remote_labels = fetch_todoist_labels(token)
        except Exception as e:
            if not remote_error:
                remote_error = str(e)

    return {
        "configured": bool(token),
        "remote_error": remote_error,
        "roles": [
            {
                "id": r.id,
                "name": r.name,
                "todoist_project_id": r.todoist_project_id,
                "todoist_project_name": r.todoist_project_name
            }
            for r in roles
        ],
        "ambitions": ambitions,
        "remote_projects": remote_projects,
        "remote_labels": remote_labels
    }

@app.post("/todoist/mappings/role")
def map_role_to_todoist(req: RoleTodoistMappingRequest, db: Session = Depends(get_db)):
    role = crud.get_role(db, req.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if req.create_new:
        token = get_todoist_token(db)
        if not token:
            raise HTTPException(status_code=400, detail="Todoist token not configured")
        try:
            proj = create_todoist_project(token, role.name)
            role.todoist_project_id = str(proj.get("id"))
            role.todoist_project_name = proj.get("name", role.name)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create Todoist project: {e}")
    else:
        role.todoist_project_id = req.todoist_project_id or None
        role.todoist_project_name = req.todoist_project_name or None

    db.commit()
    db.refresh(role)
    return {
        "status": "success",
        "role": {
            "id": role.id,
            "name": role.name,
            "todoist_project_id": role.todoist_project_id,
            "todoist_project_name": role.todoist_project_name
        }
    }

@app.post("/todoist/mappings/ambition")
def map_ambition_to_todoist(req: AmbitionTodoistMappingRequest, db: Session = Depends(get_db)):
    ambition = crud.get_ambition(db, req.ambition_id)
    if not ambition:
        raise HTTPException(status_code=404, detail="Project (Ambition) not found")

    if req.create_new:
        token = get_todoist_token(db)
        if not token:
            raise HTTPException(status_code=400, detail="Todoist token not configured")
        label_name = (req.todoist_label_name or ambition.outcome).strip().replace(" ", "_")
        try:
            lbl = create_todoist_label(token, label_name)
            ambition.todoist_label_id = str(lbl.get("id"))
            ambition.todoist_label_name = lbl.get("name", label_name)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create Todoist label: {e}")
    else:
        ambition.todoist_label_id = req.todoist_label_id or None
        ambition.todoist_label_name = (req.todoist_label_name.strip() if req.todoist_label_name else None)

    db.commit()
    db.refresh(ambition)
    return {
        "status": "success",
        "ambition": {
            "id": ambition.id,
            "outcome": ambition.outcome,
            "todoist_label_id": ambition.todoist_label_id,
            "todoist_label_name": ambition.todoist_label_name
        }
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
    inbox_item = None
    # Verify inbox item exists (skip check if it's an email clarify or a direct add with id=0)
    if not request.email_id and item_id > 0:
        inbox_item = db.query(crud.models.Inbox).filter(crud.models.Inbox.id == item_id).first()
        if not inbox_item: raise HTTPException(status_code=404, detail="Inbox item not found")

    # Transfer Todoist metadata if clarifying a Todoist-sourced inbox item (Idea #6)
    todoist_tid = inbox_item.todoist_task_id if inbox_item else None
    todoist_due = inbox_item.todoist_due_date if inbox_item else None
    todoist_prio = (inbox_item.todoist_priority or 1) if inbox_item else 1
    todoist_created = inbox_item.todoist_created_at if inbox_item else None

    # Create target record
    if request.type == "task":
        new_task = crud.create_task(
            db,
            title=request.title,
            ambition_id=request.ambition_id,
            role_id=request.role_id,
            energy_level=request.energy_level,
            estimated_time=request.estimated_time,
            context_tags=request.context_tags,
            todoist_task_id=todoist_tid,
            todoist_due_date=todoist_due,
            todoist_priority=todoist_prio,
            todoist_created_at=todoist_created
        )
        if todoist_tid and get_todoist_token(db):
            try:
                export_mindwater_task_to_todoist(db, new_task)
            except Exception:
                pass
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
def get_tasks(role_id: Optional[int] = None, context: Optional[str] = None, energy: Optional[str] = None, include_archived: bool = False, db: Session = Depends(get_db)):
    tasks = crud.get_filtered_tasks(db, role_id=role_id, context_tag=context, energy_level=energy, include_archived=include_archived)
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
        "ambition": {"id": t.ambition.id, "outcome": t.ambition.outcome} if t.ambition else None,
        "todoist_task_id": t.todoist_task_id,
        "todoist_due_date": t.todoist_due_date,
        "todoist_priority": t.todoist_priority,
        "todoist_created_at": t.todoist_created_at.isoformat() if t.todoist_created_at else None
    } for t in tasks]

@app.patch("/tasks/{task_id}/status")
def toggle_task_status(task_id: int, status: str, db: Session = Depends(get_db)):
    task = crud.update_task_status(db, task_id, status)
    if task and task.todoist_task_id:
        token = get_todoist_token(db)
        if token:
            try:
                if status == "done":
                    close_todoist_task(token, str(task.todoist_task_id))
                elif status == "todo":
                    reopen_todoist_task(token, str(task.todoist_task_id))
            except Exception:
                pass
    return {"status": "success"}

@app.put("/tasks/{task_id}")
def update_task_details(task_id: int, update: TaskUpdate, db: Session = Depends(get_db)):
    task = crud.update_task(db, task_id, **update.dict(exclude_unset=True))
    if task and task.todoist_task_id and get_todoist_token(db):
        try:
            export_mindwater_task_to_todoist(db, task)
        except Exception:
            pass
    return {"status": "success"}

@app.post("/tasks/{task_id}/push-todoist")
def push_to_todoist(task_id: int, db: Session = Depends(get_db)):
    task = db.query(crud.models.Task).filter(crud.models.Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404)
    try:
        todoist_id = export_mindwater_task_to_todoist(db, task)
        return {"status": "success", "todoist_id": todoist_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/tasks/batch-push-todoist")
def batch_push_to_todoist(req: BatchPushTodoistRequest, db: Session = Depends(get_db)):
    pushed_count = 0
    errors = []
    for tid in req.task_ids:
        task = db.query(crud.models.Task).filter(crud.models.Task.id == tid).first()
        if not task:
            continue
        try:
            export_mindwater_task_to_todoist(db, task)
            pushed_count += 1
        except Exception as e:
            errors.append(f"Task {tid}: {e}")
    return {"status": "success", "pushed_count": pushed_count, "errors": errors}

# --- Horizons ---

@app.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    roles = crud.get_all_roles(db)
    return [{
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "todoist_project_id": r.todoist_project_id,
        "todoist_project_name": r.todoist_project_name
    } for r in roles]

@app.post("/roles")
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    return crud.create_h2(db, name=role.name, description=role.description)

@app.put("/roles/{role_id}")
def update_role(role_id: int, role: RoleCreate, db: Session = Depends(get_db)):
    updated = crud.update_role(db, role_id, **role.dict())
    if updated and updated.todoist_project_id:
        token = get_todoist_token(db)
        if token:
            try:
                update_todoist_project(token, str(updated.todoist_project_id), updated.name)
                updated.todoist_project_name = updated.name
                db.commit()
            except Exception:
                pass
    return updated

@app.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    crud.delete_role(db, role_id)
    return {"status": "success"}

@app.get("/ambitions")
def get_ambitions(status: str = "active", db: Session = Depends(get_db)):
    # Returning with task counts for the review/projects view
    return crud.get_ambitions_with_task_counts(db, status=status)

@app.post("/ambitions")
def create_ambition(ambition: AmbitionCreate, db: Session = Depends(get_db)):
    return crud.create_ambition(db, outcome=ambition.outcome, h2_id=ambition.h2_id)

@app.put("/ambitions/{ambition_id}")
def update_ambition(ambition_id: int, ambition: AmbitionCreate, db: Session = Depends(get_db)):
    updated = crud.update_ambition(db, ambition_id, **ambition.dict())
    if updated and updated.todoist_label_id:
        token = get_todoist_token(db)
        if token:
            try:
                new_label = updated.outcome.strip().replace(" ", "_")
                update_todoist_label(token, str(updated.todoist_label_id), new_label)
                updated.todoist_label_name = new_label
                db.commit()
            except Exception:
                pass
    return updated

@app.post("/ambitions/{ambition_id}/archive")
def archive_ambition(ambition_id: int, db: Session = Depends(get_db)):
    # Propagate archive to Todoist by closing synced active tasks (Idea #3)
    token = get_todoist_token(db)
    if token:
        linked_tasks = crud.get_tasks_by_ambition(db, ambition_id)
        for t in linked_tasks:
            if t.todoist_task_id and t.status == "todo":
                try:
                    close_todoist_task(token, str(t.todoist_task_id))
                except Exception:
                    pass
    archived = crud.archive_ambition(db, ambition_id)
    if not archived:
        raise HTTPException(status_code=404, detail="Ambition not found")
    return {"status": "success"}

@app.delete("/ambitions/{ambition_id}")
def delete_ambition(ambition_id: int, db: Session = Depends(get_db)):
    # Propagate delete to Todoist by deleting synced tasks (Idea #3)
    token = get_todoist_token(db)
    if token:
        linked_tasks = crud.get_tasks_by_ambition(db, ambition_id)
        for t in linked_tasks:
            if t.todoist_task_id:
                try:
                    delete_todoist_task(token, str(t.todoist_task_id))
                except Exception:
                    pass
    deleted = crud.delete_ambition(db, ambition_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ambition not found")
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
        "actual_time": t.actual_time,
        "todoist_task_id": t.todoist_task_id,
        "todoist_due_date": t.todoist_due_date,
        "todoist_priority": t.todoist_priority
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

@app.get("/review/stale-todoist-tasks")
def get_review_stale_todoist_tasks(days: int = 14, db: Session = Depends(get_db)):
    stale = crud.get_stale_todoist_tasks(db, days=days)
    return [{
        "id": t.id,
        "title": t.title,
        "todoist_task_id": t.todoist_task_id,
        "todoist_created_at": t.todoist_created_at.isoformat() if t.todoist_created_at else None,
        "ambition_outcome": t.ambition.outcome if t.ambition else None,
        "role_name": t.role.name if t.role else None
    } for t in stale]

# Mount the static directory at /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
