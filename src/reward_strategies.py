from abc import ABC, abstractmethod
from typing import List

from rewards import Reward, GoldReward


class RewardStrategy(ABC):
    @abstractmethod
    def calculate_rewards(self, quest, player) -> List[Reward]:
        ...


class FixedRewardStrategy(RewardStrategy):
    """Retourne toujours la même liste de récompenses."""

    def __init__(self, rewards: List[Reward]) -> None:
        self._rewards = rewards

    def calculate_rewards(self, quest, player) -> List[Reward]:
        return self._rewards


class GoldBasedOnDifficulty(RewardStrategy):
    """Récompense en or basée sur une difficulté."""

    def __init__(self, difficulty: int) -> None:
        self.difficulty = difficulty

    def calculate_rewards(self, quest, player) -> List[Reward]:
        return [GoldReward(self.difficulty * 100)]
