from typing import List

from quest_base import Quest


class ProgressionTree:
    """Permet de gérer un arbre de quêtes (main / secondaires)."""

    def __init__(self, root_quests: List[Quest]) -> None:
        self.root_quests = root_quests

    def get_main_quests(self) -> List[Quest]:
        return self.root_quests

    def get_all_quests(self) -> List[Quest]:
        all_quests: List[Quest] = []

        def visit(q: Quest) -> None:
            all_quests.append(q)
            for child in q.get_subquests():
                visit(child)

        for root in self.root_quests:
            visit(root)
        return all_quests
