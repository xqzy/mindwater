from dataclasses import dataclass, field
from typing import List, Optional, Any
from datetime import datetime

@dataclass
class HorizonBase:
    name: str
    description: str = ""
    icon: str = ""
    priority: int = 0

@dataclass
class Horizon5(HorizonBase):
    pass

@dataclass
class Horizon4(HorizonBase):
    target_date: Optional[str] = None
    h5_id: Optional[str] = None

@dataclass
class Horizon2(HorizonBase):
    h4_id: Optional[str] = None
    ambitions: List['Ambition'] = field(default_factory=list)
    tasks: List['Task'] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """Returns True if the Role (H2) has no active projects or tasks."""
        active_ambitions = [a for a in self.ambitions if a.status == "active"]
        active_tasks = [t for t in self.tasks if t.status in ["todo", "in_progress"]]
        return len(active_ambitions) == 0 and len(active_tasks) == 0

@dataclass
class Ambition:
    outcome: str
    status: str = "active"
    target_date: Optional[datetime] = None
    h2_id: Optional[str] = None
    h4_id: Optional[str] = None
    h5_id: Optional[str] = None
    tasks: List['Task'] = field(default_factory=list)

@dataclass
class Task:
    title: str
    status: str = "todo"
    estimated_time: int = 0
    due_date: Optional[datetime] = None
    context_tags: List[str] = field(default_factory=list)
    energy_level: str = "Medium"
    ambition_id: Optional[str] = None
    role_id: Optional[str] = None

@dataclass
class Inbox:
    raw_text: str
    source_tag: str = "manual"
    timestamp: datetime = field(default_factory=datetime.now)

# Re-define Role as an alias to Horizon2 for backward compatibility if needed, 
# but we focus on H2/H4/H5 for v2.
Role = Horizon2
