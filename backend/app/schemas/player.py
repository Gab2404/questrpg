from pydantic import BaseModel
from typing import List, Optional

class PlayerStatus(BaseModel):
    name: str
    level: int
    xp: int
    money: int
    inventory: List[str]
    spoken_to_npc: bool
    completed_quests: List[int]

class QuestAttempt(BaseModel):
    quest_id: int

class QuestResult(BaseModel):
    success: bool
    message: str
    rewards: Optional[dict] = None
    player_status: Optional[PlayerStatus] = None