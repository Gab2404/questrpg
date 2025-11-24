from abc import ABC, abstractmethod
from typing import Dict, List, Any


class Observer(ABC):
    @abstractmethod
    def update(self, event_type: str, data: Any) -> None:
        ...


class EventManager:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Observer]] = {}

    def subscribe(self, event_type: str, observer: Observer) -> None:
        self._subscribers.setdefault(event_type, []).append(observer)

    def unsubscribe(self, event_type: str, observer: Observer) -> None:
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                o for o in self._subscribers[event_type] if o is not observer
            ]

    def notify(self, event_type: str, data: Any) -> None:
        for observer in self._subscribers.get(event_type, []):
            observer.update(event_type, data)


class ConsoleObserver(Observer):
    """Observer qui affiche les événements dans la console."""

    def update(self, event_type: str, data: Any) -> None:
        if event_type == "quest_completed":
            quest = data["quest"]
            player = data["player"]
            xp = data["xp"]
            rewards = data["rewards"]
            print(
                "[EVENT] {0} a complété la quête '{1}' (+{2} XP, récompenses: {3})".format(
                    player.name, quest.name, xp, rewards
                )
            )
        else:
            print("[EVENT] {0}: {1}".format(event_type, data))
