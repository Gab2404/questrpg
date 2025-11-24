from abc import ABC, abstractmethod


class XpStrategy(ABC):
    @abstractmethod
    def calculate_xp(self, quest, player) -> int:
        ...


class FixedXpStrategy(XpStrategy):
    """Retourne une quantité fixe d'XP."""

    def __init__(self, amount: int) -> None:
        self.amount = amount

    def calculate_xp(self, quest, player) -> int:
        return self.amount


class LevelScaledXpStrategy(XpStrategy):
    """XP qui dépend du niveau du joueur."""

    def __init__(self, base: int) -> None:
        self.base = base

    def calculate_xp(self, quest, player) -> int:
        return self.base + player.level * 5
