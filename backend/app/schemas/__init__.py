"""
Schemas Pydantic pour validation des données
"""
from .auth import UserRegister, UserLogin, Token
from .player import PlayerStatus, QuestAttempt, QuestResult
from .quest import QuestBase, QuestCreate, QuestUpdate, QuestInDB, QuestWithStatus

__all__ = [
    'UserRegister',
    'UserLogin',
    'Token',
    'PlayerStatus',
    'QuestAttempt',
    'QuestResult',
    'QuestBase',
    'QuestCreate',
    'QuestUpdate',
    'QuestInDB',
    'QuestWithStatus'
]