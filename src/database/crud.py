from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models

# Horizon 5 (Purpose)
def create_h5(db: Session, name: str, description: str = None, icon: str = None):
    db_h5 = models.Horizon5(name=name, description=description, icon=icon)
    db.add(db_h5)
    db.commit()
    db.refresh(db_h5)
    return db_h5

def get_h5(db: Session, h5_id: int):
    return db.query(models.Horizon5).filter(models.Horizon5.id == h5_id).first()

# Horizon 4 (Vision)
def create_h4(db: Session, name: str, description: str = None, target_date: str = None, h5_id: int = None):
    db_h4 = models.Horizon4(name=name, description=description, target_date=target_date, h5_id=h5_id)
    db.add(db_h4)
    db.commit()
    db.refresh(db_h4)
    return db_h4

# Horizon 2 (Role)
def create_h2(db: Session, name: str, description: str = None, h4_id: int = None):
    db_h2 = models.Horizon2(name=name, description=description, h4_id=h4_id)
    db.add(db_h2)
    db.commit()
    db.refresh(db_h2)
    return db_h2

def get_role(db: Session, role_id: int):
    return db.query(models.Horizon2).filter(models.Horizon2.id == role_id).first()

def get_all_roles(db: Session):
    return db.query(models.Horizon2).all()

def update_role(db: Session, role_id: int, **kwargs):
    db_role = db.query(models.Horizon2).filter(models.Horizon2.id == role_id).first()
    if db_role:
        for key, value in kwargs.items():
            if hasattr(db_role, key):
                setattr(db_role, key, value)
        db.commit()
        db.refresh(db_role)
    return db_role

def get_roles_with_ambition_counts(db: Session):
    """
    Returns a list of tuples: (Role object, active_ambition_count)
    """
    roles = db.query(models.Horizon2).all()
    results = []
    for role in roles:
        active_count = db.query(models.Ambition).filter(
            models.Ambition.h2_id == role.id,
            models.Ambition.status == "active"
        ).count()
        results.append((role, active_count))
    return results

# Ambition (Horizon 1)
def create_ambition(db: Session, outcome: str, h2_id: int = None, h4_id: int = None, h5_id: int = None):
    db_ambition = models.Ambition(outcome=outcome, h2_id=h2_id, h4_id=h4_id, h5_id=h5_id)
    db.add(db_ambition)
    db.commit()
    db.refresh(db_ambition)
    return db_ambition

def get_ambition(db: Session, ambition_id: int):
    return db.query(models.Ambition).filter(models.Ambition.id == ambition_id).first()

def get_all_ambitions(db: Session):
    return db.query(models.Ambition).all()

def update_ambition(db: Session, ambition_id: int, **kwargs):
    db_ambition = db.query(models.Ambition).filter(models.Ambition.id == ambition_id).first()
    if db_ambition:
        for key, value in kwargs.items():
            if hasattr(db_ambition, key):
                setattr(db_ambition, key, value)
        db.commit()
        db.refresh(db_ambition)
    return db_ambition

def get_ambitions_by_role(db: Session, h2_id: int):
    return db.query(models.Ambition).filter(models.Ambition.h2_id == h2_id).all()

def get_ambitions_with_task_counts(db: Session, status: str = "active"):
    """
    Returns a list of dicts with ambition data and its todo task count.
    """
    ambitions = db.query(models.Ambition).filter(models.Ambition.status == status).all()
    results = []
    for a in ambitions:
        todo_count = db.query(models.Task).filter(
            models.Task.ambition_id == a.id,
            models.Task.status == "todo"
        ).count()
        results.append({
            "id": a.id,
            "outcome": a.outcome,
            "role_name": a.role.name if a.role else "",
            "status": a.status,
            "todo_count": todo_count
        })
    return results

def get_ambition_stats(db: Session, ambition_id: int):
    """
    Returns statistics for a specific ambition:
    - total_hours_spent: Sum of actual_time (or estimated_time if actual is 0) of done tasks.
    - finished_last_2_weeks: Count of tasks completed in the last 14 days.
    - finished_last_6_weeks: Count of tasks completed in the last 42 days.
    """
    now = datetime.now(UTC)
    # Ensure now is naive if comparison targets are naive, but we want aware
    # SQLite/SQLAlchemy might return naive. Let's handle both.
    two_weeks_ago = now - timedelta(days=14)
    six_weeks_ago = now - timedelta(days=42)

    tasks = db.query(models.Task).filter(
        models.Task.ambition_id == ambition_id,
        models.Task.status == "done"
    ).all()

    total_minutes = sum((t.actual_time if t.actual_time > 0 else t.estimated_time) for t in tasks)
    total_hours = total_minutes / 60.0

    count_2w = 0
    count_6w = 0
    for t in tasks:
        if t.completed_at:
            # Handle potential naive/aware comparison
            cat = t.completed_at
            if cat.tzinfo is None:
                cat = cat.replace(tzinfo=UTC)
            
            if cat >= two_weeks_ago:
                count_2w += 1
            if cat >= six_weeks_ago:
                count_6w += 1
    
    return {
        "total_hours": round(total_hours, 1),
        "finished_2w": count_2w,
        "finished_6w": count_6w,
        "total_finished": len(tasks)
    }

# Task (Horizon 0)
def create_task(db: Session, title: str, ambition_id: int = None, role_id: int = None, context_tags: list = None, energy_level: str = "Medium", planned_date: datetime = None, estimated_time: int = 0):
    db_task = models.Task(
        title=title, 
        ambition_id=ambition_id, 
        role_id=role_id, 
        context_tags=context_tags, 
        energy_level=energy_level,
        planned_date=planned_date,
        estimated_time=estimated_time
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_all_tasks(db: Session):
    return db.query(models.Task).all()

def get_tasks_by_ambition(db: Session, ambition_id: int):
    return db.query(models.Task).filter(models.Task.ambition_id == ambition_id).all()

def update_task_status(db: Session, task_id: int, status: str):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db_task.status = status
        if status == "done":
            db_task.completed_at = datetime.now(UTC)
        else:
            db_task.completed_at = None
        db.commit()
        db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, **kwargs):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        for key, value in kwargs.items():
            if hasattr(db_task, key):
                setattr(db_task, key, value)
        if "status" in kwargs and kwargs["status"] == "done":
            if not db_task.completed_at: # Only set if not already set
                db_task.completed_at = datetime.now(UTC)
        elif "status" in kwargs and kwargs["status"] != "done":
            db_task.completed_at = None
        db.commit()
        db.refresh(db_task)
    return db_task

def filter_tasks(db: Session, context_tag: str = None, energy_level: str = None):
    query = db.query(models.Task)
    if context_tag:
        query = query.filter(models.Task.context_tags.contains([context_tag]))
    if energy_level:
        query = query.filter(models.Task.energy_level == energy_level)
    return query.all()

def get_filtered_tasks(db: Session, role_id: int = None, context_tag: str = None, energy_level: str = None):
    query = db.query(models.Task)
    if role_id:
        query = query.filter(models.Task.role_id == role_id)
    if context_tag:
        # Using a simple check for context tags in the JSON array
        query = query.filter(models.Task.context_tags.contains([context_tag]))
    if energy_level:
        query = query.filter(models.Task.energy_level == energy_level)
    return query.all()

def get_unique_contexts(db: Session):
    tasks = db.query(models.Task).all()
    contexts = set()
    for t in tasks:
        if t.context_tags:
            for c in t.context_tags:
                contexts.add(c)
    return sorted(list(contexts))

# Inbox (Capture)
def create_inbox_item(db: Session, raw_text: str, source_tag: str = "manual"):
    db_inbox = models.Inbox(raw_text=raw_text, source_tag=source_tag)
    db.add(db_inbox)
    db.commit()
    db.refresh(db_inbox)
    return db_inbox

def delete_role(db: Session, role_id: int):
    db_role = db.query(models.Horizon2).filter(models.Horizon2.id == role_id).first()
    if db_role:
        db.delete(db_role)
        db.commit()
    return db_role

def delete_ambition(db: Session, ambition_id: int):
    db_ambition = db.query(models.Ambition).filter(models.Ambition.id == ambition_id).first()
    if db_ambition:
        db.delete(db_ambition)
        db.commit()
    return db_ambition

# Review
def record_review(db: Session):
    db_review = models.ReviewLog()
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_last_review(db: Session):
    return db.query(models.ReviewLog).order_by(models.ReviewLog.timestamp.desc()).first()

# Empty Role Check
def get_empty_roles(db: Session):
    roles = db.query(models.Horizon2).all()
    empty_roles = []
    for role in roles:
        active_ambitions = [a for a in role.ambitions if a.status == "active"]
        active_tasks = [t for t in role.tasks if t.status in ["todo", "in_progress"]]
        if not active_ambitions and not active_tasks:
            empty_roles.append(role)
    return empty_roles


