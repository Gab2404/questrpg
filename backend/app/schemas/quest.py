from pydantic import BaseModel
from typing import List, Optional, Any  # ← Ajout de Any

class Decorator(BaseModel):
    type: str
    value: Any  

class QuestBase(BaseModel):
    title: str
    description: str
    base_xp: int
    type: str
    decorators: List[Decorator] = []

class QuestCreate(QuestBase):
    pass

class QuestUpdate(QuestBase):
    pass

class QuestInDB(QuestBase):
    id: int

class QuestWithStatus(QuestInDB):
    is_completed: bool
    can_start: bool
    missing_requirements: List[str] = []