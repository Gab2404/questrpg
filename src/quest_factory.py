from typing import List

from quest_types import CollectQuest, ExplorationQuest, CombatQuest, CompositeQuest
from quest_base import Quest
from xp_strategies import FixedXpStrategy, LevelScaledXpStrategy
from reward_strategies import FixedRewardStrategy, GoldBasedOnDifficulty
from rewards import GoldReward, ItemReward


class QuestFactory:
    """Fabrique de quêtes pour centraliser leur création."""

    @staticmethod
    def create_collect_quest(
        name: str,
        description: str,
        item_name: str,
        amount: int,
    ) -> CollectQuest:
        xp_strategy = FixedXpStrategy(100)
        reward_strategy = FixedRewardStrategy(
            [GoldReward(50), ItemReward("{0} rare".format(item_name))]
        )
        return CollectQuest(
            name=name,
            description=description,
            item_name=item_name,
            required_amount=amount,
            xp_strategy=xp_strategy,
            reward_strategy=reward_strategy,
        )

    @staticmethod
    def create_combat_quest(
        name: str,
        description: str,
        enemy_name: str,
        kills: int,
        difficulty: int = 2,
    ) -> CombatQuest:
        """
        Crée une CombatQuest avec des strategies par défaut.
        """
        xp_strategy = LevelScaledXpStrategy(150)
        reward_strategy = GoldBasedOnDifficulty(difficulty)
        return CombatQuest(
            name=name,
            description=description,
            enemy_name=enemy_name,
            required_kills=kills,
            xp_strategy=xp_strategy,
            reward_strategy=reward_strategy,
        )

    @staticmethod
    def create_main_quest(
        name: str,
        description: str,
        subquests: list,
    ) -> CompositeQuest:
        """
        Crée une quête principale (Composite) et y ajoute les sous-quêtes passées.
        """
        # strategies par défaut pour la quête principale
        xp_strategy = FixedXpStrategy(500)
        reward_strategy = GoldBasedOnDifficulty(5)

        main_quest = CompositeQuest(
            name=name,
            description=description,
            xp_strategy=xp_strategy,
            reward_strategy=reward_strategy,
        )

        # ajouter les sous-quêtes via add_subquest (méthode du Composite)
        for q in subquests:
            main_quest.add_subquest(q)

        return main_quest
