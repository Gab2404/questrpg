from dataclasses import dataclass, field
from typing import List

@dataclass
class User:
    """Représente un utilisateur du système"""
    username: str
    hashed_password: str
    is_admin: bool = False
    
    # Données du joueur (pattern conservé de Player)
    name: str = "Héros"
    level: int = 1
    xp: int = 0
    money: int = 100
    inventory: List[str] = field(default_factory=list)
    spoken_to_npc: bool = False
    completed_quests: List[int] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "username": self.username,
            "hashed_password": self.hashed_password,
            "is_admin": self.is_admin,
            "name": self.name,
            "level": self.level,
            "xp": self.xp,
            "money": self.money,
            "inventory": self.inventory,
            "spoken_to_npc": self.spoken_to_npc,
            "completed_quests": self.completed_quests
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crée une instance depuis un dictionnaire"""
        return cls(**data)
    
    def add_xp(self, amount: int) -> dict:
        """Ajoute de l'XP et gère les level-ups"""
        self.xp += amount
        leveled_up = False
        
        while self.xp >= 100 * self.level:
            self.level += 1
            self.xp = 0
            leveled_up = True
        
        return {
            "xp_gained": amount,
            "leveled_up": leveled_up,
            "new_level": self.level if leveled_up else None
        }