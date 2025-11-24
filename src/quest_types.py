from typing import List

from quest_base import Quest


class CollectQuest(Quest):
    """Quête de collecte d'objets."""

    def __init__(self, item_name: str, required_amount: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.item_name = item_name
        self.required_amount = required_amount
        self.current_amount = 0

    def add_item(self, amount: int = 1) -> None:
        self.current_amount += amount

    def is_completed(self) -> bool:
        return self.current_amount >= self.required_amount


class ExplorationQuest(Quest):
    """Quête d'exploration d'un lieu."""

    def __init__(self, location: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.location = location
        self.visited = False

    def mark_visited(self) -> None:
        self.visited = True

    def is_completed(self) -> bool:
        return self.visited


class CombatQuest(Quest):
    """Quête de combat contre des ennemis."""

    def __init__(self, enemy_name: str, required_kills: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.enemy_name = enemy_name
        self.required_kills = required_kills
        self.current_kills = 0

    def add_kill(self, count: int = 1) -> None:
        self.current_kills += count

    def is_completed(self) -> bool:
        return self.current_kills >= self.required_kills


class CompositeQuest(Quest):
    """Quête composée de sous-quêtes (main / secondaires)."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._subquests: List[Quest] = []

    def add_subquest(self, quest: Quest) -> None:
        self._subquests.append(quest)
        quest.parent = self

    def get_subquests(self) -> List[Quest]:
        return self._subquests

    def is_completed(self) -> bool:
        return all(q.is_completed() for q in self._subquests)
