from dataclasses import dataclass, field
from typing import List

@dataclass
class Player:
    """Représente le joueur (Context dans le pattern)"""
    name: str = "Héros"
    level: int = 1
    xp: int = 0
    money: int = 0
    inventory: List[str] = field(default_factory=list)
    spoken_to_npc: bool = False
    completed_quests: List[int] = field(default_factory=list)

    def add_xp(self, amount: int):
        """Ajoute de l'XP et gère les level-ups"""
        self.xp += amount
        print(f"✨ {self.name} gagne {amount} XP!")
        if self.xp >= 100 * self.level:
            self.level += 1
            self.xp = 0
            print(f"🆙 LEVEL UP! Niveau {self.level} atteint!")