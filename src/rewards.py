class Reward:
    """Classe de base abstraite pour une récompense."""
    pass


class GoldReward(Reward):
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __repr__(self) -> str:
        return "{0} or".format(self.amount)


class ItemReward(Reward):
    def __init__(self, item_name: str) -> None:
        self.item_name = item_name

    def __repr__(self) -> str:
        return "Objet({0})".format(self.item_name)
