import json
import os
from typing import List
from models.quest_interfaces import IQuest
from quests.base_quest import BaseQuest
from decorators.requirements import LevelRequirementDecorator, NPCInteractionDecorator
from decorators.rewards import MoneyRewardDecorator, ItemRewardDecorator

class QuestFactory:
    """Factory pour créer des quêtes depuis le JSON"""
    
    @staticmethod
    def load_from_json(filepath: str = "data/quests_db.json") -> List[IQuest]:
        """Charge toutes les quêtes depuis le fichier JSON"""
        if not os.path.exists(filepath):
            return []
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
        except Exception:
            return []
        
        loaded_quests = []
        for q_data in data:
            quest = BaseQuest(
                quest_id=q_data["id"],
                title=q_data["title"],
                description=q_data["description"],
                base_xp=q_data["base_xp"],
                is_primary=(q_data["type"] == "PRIMARY")
            )
            
            # Application des décorateurs dans l'ordre
            for dec in q_data.get("decorators", []):
                dtype, val = dec["type"], dec["value"]
                
                if dtype == "level_req":
                    quest = LevelRequirementDecorator(quest, int(val))
                elif dtype == "npc_req":
                    quest = NPCInteractionDecorator(quest, str(val))
                elif dtype == "money_reward":
                    quest = MoneyRewardDecorator(quest, int(val))
                elif dtype == "item_reward":
                    quest = ItemRewardDecorator(quest, str(val))
            
            loaded_quests.append(quest)
        
        return loaded_quests