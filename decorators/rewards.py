from decorators.quest_decorator import QuestDecorator
from models.quest_interfaces import IQuest

class MoneyRewardDecorator(QuestDecorator):
    """Ajoute une récompense en argent"""
    
    def __init__(self, quest: IQuest, amount: int):
        super().__init__(quest)
        self.amount = amount
    
    def get_description(self) -> str:
        return super().get_description() + f" | Récompense: {self.amount} pièces"
    
    def complete(self, player):
        super().complete(player)
        player.money += self.amount
        print(f"💰 Vous recevez {self.amount} pièces d'or.")


class ItemRewardDecorator(QuestDecorator):
    """Ajoute une récompense sous forme d'objet"""
    
    def __init__(self, quest: IQuest, item_name: str):
        super().__init__(quest)
        self.item_name = item_name
    
    def get_description(self) -> str:
        return super().get_description() + f" | Récompense: {self.item_name}"
    
    def complete(self, player):
        super().complete(player)
        player.inventory.append(self.item_name)
        print(f"🎁 Vous recevez un objet : {self.item_name}")
