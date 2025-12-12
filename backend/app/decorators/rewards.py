from app.decorators.quest_decorator import QuestDecorator
from app.models.quest_interfaces import IQuest

class MoneyRewardDecorator(QuestDecorator):
    """Ajoute une récompense en argent (conservé)"""
    
    def __init__(self, quest: IQuest, amount: int):
        super().__init__(quest)
        self.amount = amount
    
    def get_description(self) -> str:
        return super().get_description() + f" | Récompense: {self.amount} pièces"
    
    def complete(self, player) -> bool:
        result = super().complete(player)
        if result:
            player.money += self.amount
        return result


class ItemRewardDecorator(QuestDecorator):
    """Ajoute une récompense sous forme d'objet (conservé)"""
    
    def __init__(self, quest: IQuest, item_name: str):
        super().__init__(quest)
        self.item_name = item_name
    
    def get_description(self) -> str:
        return super().get_description() + f" | Récompense: {self.item_name}"
    
    def complete(self, player) -> bool:
        result = super().complete(player)
        if result:
            player.inventory.append(self.item_name)
        return result