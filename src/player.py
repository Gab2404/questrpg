from typing import List

from quest_base import Quest


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.level = 1
        self.xp = 0
        self.active_quests: List[Quest] = []
        self.completed_quests: List[Quest] = []

    def accept_quest(self, quest: Quest) -> None:
        if quest in self.active_quests:
            return
        self.active_quests.append(quest)
        quest.on_accepted(self)

    def complete_quest(self, quest: Quest) -> None:
        if quest not in self.active_quests:
            return
        if not quest.is_completed():
            # On ne valide pas une quête non terminée.
            return

        xp = quest.give_xp(self)
        rewards = quest.give_rewards(self)
        self.xp += xp

        self.active_quests.remove(quest)
        self.completed_quests.append(quest)

        quest.on_completed(self, xp, rewards)

    def __repr__(self) -> str:
        return "Player(name={0}, level={1}, xp={2})".format(
            self.name, self.level, self.xp
        )
