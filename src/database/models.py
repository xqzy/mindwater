from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, UTC

Base = declarative_base()

class Horizon5(Base):
    __tablename__ = 'h5_purpose'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    icon = Column(String)
    visions = relationship("Horizon4", back_populates="purpose")
    ambitions = relationship("Ambition", back_populates="purpose")

class Horizon4(Base):
    __tablename__ = 'h4_vision'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    target_date = Column(String)
    h5_id = Column(Integer, ForeignKey('h5_purpose.id'))
    purpose = relationship("Horizon5", back_populates="visions")
    roles = relationship("Horizon2", back_populates="vision")
    ambitions = relationship("Ambition", back_populates="vision")

class Horizon2(Base):
    __tablename__ = 'h2_role'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    h4_id = Column(Integer, ForeignKey('h4_vision.id'))
    vision = relationship("Horizon4", back_populates="roles")
    ambitions = relationship("Ambition", back_populates="role")
    tasks = relationship("Task", back_populates="role")

class Ambition(Base):
    __tablename__ = 'ambition'
    id = Column(Integer, primary_key=True)
    outcome = Column(String, nullable=False)
    status = Column(String, default="active")
    h2_id = Column(Integer, ForeignKey('h2_role.id'))
    h4_id = Column(Integer, ForeignKey('h4_vision.id'))
    h5_id = Column(Integer, ForeignKey('h5_purpose.id'))
    role = relationship("Horizon2", back_populates="ambitions")
    vision = relationship("Horizon4", back_populates="ambitions")
    purpose = relationship("Horizon5", back_populates="ambitions")
    tasks = relationship("Task", back_populates="ambition")

class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(String, default="todo")
    context_tags = Column(JSON)
    energy_level = Column(String, default="Medium")
    planned_date = Column(DateTime)
    estimated_time = Column(Integer, default=0) # in minutes
    actual_time = Column(Integer, default=0)    # in minutes
    completed_at = Column(DateTime)
    ambition_id = Column(Integer, ForeignKey('ambition.id'))
    role_id = Column(Integer, ForeignKey('h2_role.id'))
    ambition = relationship("Ambition", back_populates="tasks")
    role = relationship("Horizon2", back_populates="tasks")

class ReviewLog(Base):
    __tablename__ = 'review_log'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))

class Inbox(Base):
    __tablename__ = 'inbox'
    id = Column(Integer, primary_key=True)
    raw_text = Column(String, nullable=False)
    source_tag = Column(String, default="manual")
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))

class DismissedEmail(Base):
    __tablename__ = 'dismissed_email'
    id = Column(Integer, primary_key=True)
    email_id = Column(String, unique=True, nullable=False) # Message-ID or UID
    dismissed_at = Column(DateTime, default=lambda: datetime.now(UTC))
