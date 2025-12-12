from app.models.quest_interfaces import IQuest

class QuestDecorator(IQuest):
    """Décorateur abstrait (conservé de votre code)"""
    
    def __init__(self, quest: IQuest):
        self._quest = quest
    
    def get_id(self) -> int:
        return self._quest.get_id()
    
    def get_description(self) -> str:
        return self._quest.get_description()
    
    def is_completed(self, player) -> bool:
        return self._quest.is_completed(player)
    
    def can_start(self, player) -> bool:
        return self._quest.can_start(player)
    
    def complete(self, player) -> bool:
        return self._quest.complete(player)