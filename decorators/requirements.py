from decorators.quest_decorator import QuestDecorator
from models.quest_interfaces import IQuest

class LevelRequirementDecorator(QuestDecorator):
    """Ajoute une condition de niveau minimum"""
    
    def __init__(self, quest: IQuest, min_level: int):
        super().__init__(quest)
        self.min_level = min_level
    
    def get_description(self) -> str:
        return super().get_description() + f" [Requis: Niv {self.min_level}]"
    
    def can_start(self, player) -> bool:
        if self.is_completed(player):
            return False
        
        if player.level >= self.min_level:
            return super().can_start(player)
        
        print(f"⛔ Niveau insuffisant. Requis: {self.min_level}, Actuel: {player.level}")
        return False


class NPCInteractionDecorator(QuestDecorator):
    """Ajoute une condition de dialogue avec un PNJ"""
    
    def __init__(self, quest: IQuest, npc_name: str):
        super().__init__(quest)
        self.npc_name = npc_name
    
    def get_description(self) -> str:
        return super().get_description() + f" [Requis: Parler à {self.npc_name}]"
    
    def can_start(self, player) -> bool:
        if self.is_completed(player):
            return False
        
        if player.spoken_to_npc:
            return super().can_start(player)
        
        print(f"⛔ Vous devez d'abord parler à {self.npc_name} !")
        return False
