from models.quest_interfaces import IQuest

class QuestDecorator(IQuest):
    """Décorateur abstrait (Wrapper dans le pattern Decorator)"""
    
    def __init__(self, quest: IQuest):
        self._quest = quest
    
    def get_id(self) -> int:
        """Délègue l'appel à la quête wrappée"""
        return self._quest.get_id()
    
    def get_description(self) -> str:
        """Délègue l'appel à la quête wrappée"""
        return self._quest.get_description()
    
    def is_completed(self, player) -> bool:
        """Délègue l'appel à la quête wrappée"""
        return self._quest.is_completed(player)
    
    def can_start(self, player) -> bool:
        """Délègue l'appel à la quête wrappée"""
        return self._quest.can_start(player)
    
    def complete(self, player):
        """Délègue l'appel à la quête wrappée"""
        self._quest.complete(player)