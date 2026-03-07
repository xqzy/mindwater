from sqlalchemy.orm import Session
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

# Ambition (Horizon 1)
def create_ambition(db: Session, outcome: str, h2_id: int = None, h4_id: int = None, h5_id: int = None):
    db_ambition = models.Ambition(outcome=outcome, h2_id=h2_id, h4_id=h4_id, h5_id=h5_id)
    db.add(db_ambition)
    db.commit()
    db.refresh(db_ambition)
    return db_ambition

def get_ambitions_by_role(db: Session, h2_id: int):
    return db.query(models.Ambition).filter(models.Ambition.h2_id == h2_id).all()

# Task (Horizon 0)
def create_task(db: Session, title: str, ambition_id: int = None, role_id: int = None, context_tags: list = None, energy_level: str = "Medium"):
    db_task = models.Task(title=title, ambition_id=ambition_id, role_id=role_id, context_tags=context_tags, energy_level=energy_level)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_by_ambition(db: Session, ambition_id: int):
    return db.query(models.Task).filter(models.Task.ambition_id == ambition_id).all()

def filter_tasks(db: Session, context_tag: str = None, energy_level: str = None):
    query = db.query(models.Task)
    if context_tag:
        query = query.filter(models.Task.context_tags.contains([context_tag]))
    if energy_level:
        query = query.filter(models.Task.energy_level == energy_level)
    return query.all()

# Inbox (Capture)
def create_inbox_item(db: Session, raw_text: str, source_tag: str = "manual"):
    db_inbox = models.Inbox(raw_text=raw_text, source_tag=source_tag)
    db.add(db_inbox)
    db.commit()
    db.refresh(db_inbox)
    return db_inbox

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
