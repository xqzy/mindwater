import os
import json
import httpx
from datetime import datetime, UTC
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from src.database import crud, models

load_dotenv()

TODOIST_BASE_URL = "https://api.todoist.com/api/v1"
TODOIST_API_URL = f"{TODOIST_BASE_URL}/tasks"


def _extract_list(payload: Any) -> List[Dict[str, Any]]:
    """
    Handles both Todoist Unified API v1 paginated dict responses
    ({'results': [...], 'next_cursor': ...}) and plain list responses.
    """
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return payload["results"]
    return []


def _fetch_paginated(client: httpx.Client, url: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    cursor: Optional[str] = None
    while True:
        params = {"cursor": cursor} if cursor else None
        resp = client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        items.extend(_extract_list(data))
        if isinstance(data, dict) and data.get("next_cursor"):
            cursor = data["next_cursor"]
        else:
            break
    return items


def get_todoist_token(db: Optional[Session] = None) -> Optional[str]:
    """
    Retrieves the Todoist API token.
    Priority:
    1. Sticky DB setting ('todoist_api_token' in app_setting table)
    2. Credentials JSON file referenced by FIREBASE_CREDENTIALS / mindwater-*.json
    3. Environment variable TODOIST_API_TOKEN
    """
    if db is not None:
        try:
            db_token = crud.get_setting(db, "todoist_api_token")
            if db_token and db_token.strip():
                return db_token.strip()
        except Exception:
            pass

    cred_path = os.environ.get("FIREBASE_CREDENTIALS")
    if not cred_path:
        import glob
        matches = glob.glob("mindwater-*.json")
        if matches:
            cred_path = matches[0]

    if cred_path and os.path.exists(cred_path):
        try:
            with open(cred_path, "r") as f:
                creds = json.load(f)
                token = creds.get("todoist_api_token")
                if token:
                    return token
        except Exception:
            pass

    return os.environ.get("TODOIST_API_TOKEN")


def mask_token(token: Optional[str]) -> str:
    if not token:
        return ""
    token = token.strip()
    if len(token) <= 4:
        return "••••"
    return "••••••••••••" + token[-4:]


def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _parse_iso_datetime(val: Optional[str]) -> Optional[datetime]:
    if not val:
        return None
    try:
        if val.endswith("Z"):
            val = val[:-1] + "+00:00"
        return datetime.fromisoformat(val)
    except Exception:
        return None


# --- Projects API (Mapped to Mindwater Roles / H2) ---

def fetch_todoist_projects(token: str) -> List[Dict[str, Any]]:
    with httpx.Client(timeout=15.0) as client:
        return _fetch_paginated(client, f"{TODOIST_BASE_URL}/projects", _headers(token))


def create_todoist_project(token: str, name: str) -> Dict[str, Any]:
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(
            f"{TODOIST_BASE_URL}/projects",
            headers=_headers(token),
            json={"name": name}
        )
        resp.raise_for_status()
        return resp.json()


def update_todoist_project(token: str, project_id: str, name: str) -> Dict[str, Any]:
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(
            f"{TODOIST_BASE_URL}/projects/{project_id}",
            headers=_headers(token),
            json={"name": name}
        )
        resp.raise_for_status()
        return resp.json()


# --- Labels API (Mapped to Mindwater Projects / Ambitions / H1) ---

def fetch_todoist_labels(token: str) -> List[Dict[str, Any]]:
    with httpx.Client(timeout=15.0) as client:
        return _fetch_paginated(client, f"{TODOIST_BASE_URL}/labels", _headers(token))


def create_todoist_label(token: str, name: str) -> Dict[str, Any]:
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(
            f"{TODOIST_BASE_URL}/labels",
            headers=_headers(token),
            json={"name": name}
        )
        resp.raise_for_status()
        return resp.json()


def update_todoist_label(token: str, label_id: str, name: str) -> Dict[str, Any]:
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(
            f"{TODOIST_BASE_URL}/labels/{label_id}",
            headers=_headers(token),
            json={"name": name}
        )
        resp.raise_for_status()
        return resp.json()


# --- Tasks API ---

def fetch_todoist_tasks(token: str) -> List[Dict[str, Any]]:
    with httpx.Client(timeout=15.0) as client:
        return _fetch_paginated(client, TODOIST_API_URL, _headers(token))


def push_task_to_todoist(
    title: str,
    due_date: Any = None,
    project_id: Optional[str] = None,
    labels: Optional[List[str]] = None,
    duration_minutes: Optional[int] = None,
    db: Optional[Session] = None
) -> str:
    """
    Pushes a task to Todoist using REST API v2.
    """
    token = get_todoist_token(db=db)
    if not token:
        raise ValueError("Todoist API token not found. Configure it in the Todoist tab.")

    data: Dict[str, Any] = {"content": title}

    if due_date:
        if isinstance(due_date, datetime):
            data["due_date"] = due_date.strftime("%Y-%m-%d")
        elif isinstance(due_date, str):
            data["due_date"] = due_date[:10]

    if project_id:
        data["project_id"] = str(project_id)

    if labels:
        data["labels"] = [lbl for lbl in labels if lbl]

    if duration_minutes and int(duration_minutes) > 0:
        data["duration"] = int(duration_minutes)
        data["duration_unit"] = "minute"

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(TODOIST_API_URL, headers=_headers(token), json=data)
            response.raise_for_status()
            result = response.json()
            return str(result.get("id"))
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Todoist API error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        raise RuntimeError(f"Failed to push to Todoist: {str(e)}")


def update_todoist_task(
    token: str,
    todoist_task_id: str,
    title: Optional[str] = None,
    due_date: Any = None,
    labels: Optional[List[str]] = None,
    duration_minutes: Optional[int] = None
) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    if title is not None:
        data["content"] = title
    if due_date is not None:
        if isinstance(due_date, datetime):
            data["due_date"] = due_date.strftime("%Y-%m-%d")
        elif isinstance(due_date, str) and due_date:
            data["due_date"] = due_date[:10]
    if labels is not None:
        data["labels"] = [lbl for lbl in labels if lbl]
    if duration_minutes is not None and int(duration_minutes) > 0:
        data["duration"] = int(duration_minutes)
        data["duration_unit"] = "minute"

    with httpx.Client(timeout=15.0) as client:
        resp = client.post(
            f"{TODOIST_API_URL}/{todoist_task_id}",
            headers=_headers(token),
            json=data
        )
        resp.raise_for_status()
        return resp.json()


def close_todoist_task(token: str, todoist_task_id: str) -> bool:
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(
            f"{TODOIST_API_URL}/{todoist_task_id}/close",
            headers=_headers(token)
        )
        resp.raise_for_status()
        return True


def reopen_todoist_task(token: str, todoist_task_id: str) -> bool:
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(
            f"{TODOIST_API_URL}/{todoist_task_id}/reopen",
            headers=_headers(token)
        )
        resp.raise_for_status()
        return True


def delete_todoist_task(token: str, todoist_task_id: str) -> bool:
    with httpx.Client(timeout=15.0) as client:
        resp = client.delete(
            f"{TODOIST_API_URL}/{todoist_task_id}",
            headers=_headers(token)
        )
        resp.raise_for_status()
        return True


def export_mindwater_task_to_todoist(db: Session, task: models.Task) -> str:
    """
    Exports or updates a Mindwater Task in Todoist, applying Role -> Todoist Project
    and Ambition -> Todoist Label mappings plus duration and due date.
    """
    token = get_todoist_token(db=db)
    if not token:
        raise ValueError("Todoist API token not configured.")

    project_id = None
    if task.role_id:
        role = crud.get_role(db, task.role_id)
        if role and role.todoist_project_id:
            project_id = role.todoist_project_id

    labels = []
    if task.ambition_id:
        amb = crud.get_ambition(db, task.ambition_id)
        if amb and amb.todoist_label_name:
            labels.append(amb.todoist_label_name)
            if not project_id and amb.h2_id:
                amb_role = crud.get_role(db, amb.h2_id)
                if amb_role and amb_role.todoist_project_id:
                    project_id = amb_role.todoist_project_id

    due_val = task.planned_date or task.todoist_due_date

    if task.todoist_task_id:
        update_todoist_task(
            token=token,
            todoist_task_id=str(task.todoist_task_id),
            title=task.title,
            due_date=due_val,
            labels=labels,
            duration_minutes=task.estimated_time
        )
        return str(task.todoist_task_id)
    else:
        todoist_id = push_task_to_todoist(
            title=task.title,
            due_date=due_val,
            project_id=project_id,
            labels=labels,
            duration_minutes=task.estimated_time,
            db=db
        )
        task.todoist_task_id = str(todoist_id)
        if not task.todoist_created_at:
            task.todoist_created_at = datetime.now(UTC)
        db.commit()
        db.refresh(task)
        return str(todoist_id)


def sync_with_todoist(db: Session) -> Dict[str, Any]:
    """
    Performs bi-directional synchronization between Todoist and Mindwater:
    1. Fetches active tasks from Todoist.
    2. Routes Todoist tasks with a mapped Label (Ambition) or mapped Project (Role)
       into Mindwater Tasks (creating or updating).
    3. Routes unmapped Todoist tasks into Mindwater Inbox (creating or updating).
    4. Marks local 'todo' Tasks with a todoist_task_id as 'done' if they are no longer
       active in Todoist (completed in Todoist), crediting completion time for stats.
    """
    token = get_todoist_token(db=db)
    if not token:
        return {"status": "skipped", "reason": "Todoist token not configured"}

    remote_tasks = fetch_todoist_tasks(token)

    # Build lookup dictionaries for mappings
    all_roles = crud.get_all_roles(db)
    role_by_todoist_proj: Dict[str, models.Horizon2] = {}
    for r in all_roles:
        if r.todoist_project_id:
            role_by_todoist_proj[str(r.todoist_project_id)] = r

    all_ambitions = crud.get_all_ambitions(db)
    ambition_by_label: Dict[str, models.Ambition] = {}
    for a in all_ambitions:
        if a.todoist_label_name and a.status != "archived":
            ambition_by_label[a.todoist_label_name.strip().lower()] = a

    active_remote_ids = set()
    imported_tasks = 0
    imported_inbox = 0
    updated_tasks = 0
    completed_tasks = 0

    for rt in remote_tasks:
        tid = str(rt.get("id"))
        active_remote_ids.add(tid)

        title = rt.get("content", "").strip()
        due_obj = rt.get("due") or {}
        due_date_str = due_obj.get("date")
        priority = int(rt.get("priority", 1))
        created_at = _parse_iso_datetime(rt.get("created_at")) or datetime.now(UTC)

        # Duration (Idea #5)
        duration_obj = rt.get("duration") or {}
        est_minutes = 0
        if duration_obj.get("amount"):
            amt = int(duration_obj["amount"])
            unit = duration_obj.get("unit", "minute")
            est_minutes = amt * 480 if unit == "day" else amt

        # Determine mapping via Labels -> Ambition and Project -> Role
        rt_labels = rt.get("labels") or []
        matched_ambition: Optional[models.Ambition] = None
        for lbl in rt_labels:
            if lbl.strip().lower() in ambition_by_label:
                matched_ambition = ambition_by_label[lbl.strip().lower()]
                break

        rt_proj_id = str(rt.get("project_id")) if rt.get("project_id") else None
        matched_role: Optional[models.Horizon2] = role_by_todoist_proj.get(rt_proj_id) if rt_proj_id else None

        target_ambition_id = matched_ambition.id if matched_ambition else None
        target_role_id = matched_role.id if matched_role else (matched_ambition.h2_id if matched_ambition else None)
        is_mapped = (target_ambition_id is not None) or (target_role_id is not None)

        existing_task = db.query(models.Task).filter(models.Task.todoist_task_id == tid).first()
        existing_inbox = db.query(models.Inbox).filter(models.Inbox.todoist_task_id == tid).first()

        if existing_task:
            existing_task.title = title
            existing_task.todoist_due_date = due_date_str
            existing_task.todoist_priority = priority
            if est_minutes > 0:
                existing_task.estimated_time = est_minutes
            if target_ambition_id is not None:
                existing_task.ambition_id = target_ambition_id
            if target_role_id is not None:
                existing_task.role_id = target_role_id
            if existing_inbox:
                db.delete(existing_inbox)
            updated_tasks += 1
        elif is_mapped:
            # Mapped task -> goes directly to Mindwater Tasks (removing from Inbox if previously unmapped)
            if existing_inbox:
                db.delete(existing_inbox)
            new_task = models.Task(
                title=title,
                status="todo",
                ambition_id=target_ambition_id,
                role_id=target_role_id,
                estimated_time=est_minutes,
                todoist_task_id=tid,
                todoist_due_date=due_date_str,
                todoist_priority=priority,
                todoist_created_at=created_at
            )
            db.add(new_task)
            imported_tasks += 1
        else:
            # Unmapped task -> goes to Mindwater Inbox for clarifying
            if existing_inbox:
                existing_inbox.raw_text = title
                existing_inbox.todoist_due_date = due_date_str
                existing_inbox.todoist_priority = priority
            else:
                new_inbox = models.Inbox(
                    raw_text=title,
                    source_tag="todoist",
                    todoist_task_id=tid,
                    todoist_due_date=due_date_str,
                    todoist_priority=priority,
                    todoist_created_at=created_at
                )
                db.add(new_inbox)
                imported_inbox += 1

    # Two-way completion sync: Any local 'todo' task with a todoist_task_id not in active_remote_ids was completed in Todoist
    local_synced_open_tasks = db.query(models.Task).filter(
        models.Task.todoist_task_id.isnot(None),
        models.Task.status == "todo"
    ).all()
    for lt in local_synced_open_tasks:
        if str(lt.todoist_task_id) not in active_remote_ids:
            lt.status = "done"
            lt.completed_at = datetime.now(UTC)
            if (lt.actual_time or 0) == 0 and (lt.estimated_time or 0) > 0:
                lt.actual_time = lt.estimated_time
            completed_tasks += 1

    # Also clean up any Todoist-sourced Inbox items that were completed/deleted in Todoist
    local_synced_inbox = db.query(models.Inbox).filter(
        models.Inbox.todoist_task_id.isnot(None)
    ).all()
    for li in local_synced_inbox:
        if str(li.todoist_task_id) not in active_remote_ids:
            db.delete(li)

    db.commit()
    crud.set_setting(db, "last_todoist_sync", datetime.now(UTC).isoformat())

    return {
        "status": "success",
        "imported_tasks": imported_tasks,
        "imported_inbox": imported_inbox,
        "updated_tasks": updated_tasks,
        "completed_tasks": completed_tasks,
        "last_sync": crud.get_setting(db, "last_todoist_sync")
    }
