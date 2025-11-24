from abc import ABC, abstractmethod
from typing import List, Optional

from xp_strategies import XpStrategy
from reward_strategies import RewardStrategy
from rewards import Reward
from events import EventManager


class Quest(ABC):
    """Classe de base pour toutes les quêtes."""

    def __init__(
        self,
        name: str,
        description: str,
        xp_strategy: XpStrategy,
        reward_strategy: RewardStrategy,
    ) -> None:
        self.name = name
        self.description = description
        self.xp_strategy = xp_strategy
        self.reward_strategy = reward_strategy
        self.parent = None  # type: Optional["Quest"]
        self.event_manager = None  # type: Optional[EventManager]

    def set_event_manager(self, event_manager: EventManager) -> None:
        self.event_manager = event_manager

    # ----- Hooks COMPOSITE -----

    def add_subquest(self, quest: "Quest") -> None:
        """Sera surchargé par les quêtes composites."""
        raise NotImplementedError("Cette quête n'est pas composite.")

    def get_subquests(self) -> List["Quest"]:
        """Pour les quêtes non composites : pas de sous-quêtes."""
        return []

    # ----- Comportements de base -----

    @abstractmethod
    def is_completed(self) -> bool:
        """Retourne True si la quête est terminée."""
        ...

    def on_accepted(self, player) -> None:
        """Appelé quand la quête est acceptée par un joueur."""
        pass

    def on_completed(self, player, xp: int, rewards: List[Reward]) -> None:
        """Appelé quand la quête est complétée par un joueur."""
        if self.event_manager is not None:
            self.event_manager.notify(
                "quest_completed",
                {
                    "quest": self,
                    "player": player,
                    "xp": xp,
                    "rewards": rewards,
                },
            )

    def give_xp(self, player) -> int:
        return self.xp_strategy.calculate_xp(self, player)

    def give_rewards(self, player) -> List[Reward]:
        return self.reward_strategy.calculate_rewards(self, player)
