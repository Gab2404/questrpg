from models.quest_interfaces import IQuest

class BaseQuest(IQuest):
    """Implémentation de base d'une quête (Component dans Decorator)"""
    
    def __init__(self, quest_id: int, title: str, description: str, 
                 base_xp: int, is_primary: bool = True):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.base_xp = base_xp
        self.type_label = "PRINCIPALE" if is_primary else "SECONDAIRE"

    def get_id(self) -> int:
        return self.quest_id

    def is_completed(self, player) -> bool:
        return self.quest_id in player.completed_quests

    def get_description(self) -> str:
        return f"[{self.type_label}] {self.title}: {self.description} (XP: {self.base_xp})"

    def can_start(self, player) -> bool:
        if self.is_completed(player):
            print(f"✅ Vous avez déjà terminé la quête : {self.title}")
            return False
        return True

    def complete(self, player):
        print(f"\n✅ Quête terminée : {self.title}")
        player.add_xp(self.base_xp)
        if self.quest_id not in player.completed_quests:
            player.completed_quests.append(self.quest_id)