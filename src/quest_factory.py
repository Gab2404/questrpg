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
            xp_strategy=x_strategy,
            reward_strategy=reward_strategy,
        )
