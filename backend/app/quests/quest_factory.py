from typing import List, Dict
from app.models.quest_interfaces import IQuest
from app.quests.base_quest import BaseQuest
from app.decorators.requirements import LevelRequirementDecorator, NPCInteractionDecorator
from app.decorators.rewards import MoneyRewardDecorator, ItemRewardDecorator

class QuestFactory:
    """Factory pour créer des quêtes depuis le JSON"""
    
    @staticmethod
    def create_quest_from_dict(q_data: Dict) -> IQuest:
        """Crée une quête depuis un dictionnaire"""
        quest = BaseQuest(
            quest_id=q_data["id"],
            title=q_data["title"],
            description=q_data["description"],
            base_xp=q_data["base_xp"],
            is_primary=(q_data["type"] == "PRIMARY")
        )
        
        # Récupérer les décorateurs
        decorators = list(q_data.get("decorators", []))  # Copie pour modification
        
        # ✅ FIX : Les quêtes SECONDARY doivent avoir une condition
        if q_data["type"] == "SECONDARY":
            has_requirement = any(
                dec["type"] in ["level_req", "npc_req"] 
                for dec in decorators
            )
            
            # Si aucune condition, ajouter NPC par défaut
            if not has_requirement:
                decorators.insert(0, {
                    "type": "npc_req",
                    "value": "Guide"
                })
        
        # Application des décorateurs dans l'ordre
        for dec in decorators:
            dtype, val = dec["type"], dec["value"]
            
            if dtype == "level_req":
                quest = LevelRequirementDecorator(quest, int(val))
            elif dtype == "npc_req":
                quest = NPCInteractionDecorator(quest, str(val))
            elif dtype == "money_reward":
                quest = MoneyRewardDecorator(quest, int(val))
            elif dtype == "item_reward":
                quest = ItemRewardDecorator(quest, str(val))
        
        return quest
    
    @staticmethod
    def load_all_quests_from_db(quests_data: List[Dict]) -> List[IQuest]:
        """Charge toutes les quêtes depuis une liste de dictionnaires"""
        return [QuestFactory.create_quest_from_dict(q) for q in quests_data]