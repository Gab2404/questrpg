from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.player import PlayerStatus, QuestResult
from app.schemas.quest import QuestWithStatus
from app.database import db
from app.quests.quest_factory import QuestFactory
import logging

# ✅ Ajouter du logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/player", tags=["Player"])

@router.get("/status", response_model=PlayerStatus)
async def get_player_status(current_user: User = Depends(get_current_user)):
    """Récupère le statut du joueur"""
    return PlayerStatus(
        name=current_user.name,
        level=current_user.level,
        xp=current_user.xp,
        money=current_user.money,
        inventory=current_user.inventory,
        spoken_to_npc=current_user.spoken_to_npc,
        completed_quests=current_user.completed_quests
    )

@router.get("/quests", response_model=List[QuestWithStatus])
async def list_quests(current_user: User = Depends(get_current_user)):
    """Liste toutes les quêtes avec leur statut"""
    quests_data = db.get_all_quests()
    result = []
    
    # ✅ Debug: Afficher les quêtes complétées du joueur
    logger.info(f"Player {current_user.username} completed quests: {current_user.completed_quests}")
    
    for quest_data in quests_data:
        quest_id = quest_data["id"]
        
        # ✅ Debug: Vérifier si la quête est dans les complétées
        logger.info(f"Checking quest {quest_id}: in completed? {quest_id in current_user.completed_quests}")
        
        # Créer la quête avec ses décorateurs
        quest_obj = QuestFactory.create_quest_from_dict(quest_data)
        
        is_completed = quest_obj.is_completed(current_user)
        can_start = quest_obj.can_start(current_user)
        
        # ✅ Debug: Afficher les résultats
        logger.info(f"Quest {quest_id} - is_completed: {is_completed}, can_start: {can_start}")
        
        # Déterminer les conditions manquantes
        missing_requirements = []
        if not is_completed and not can_start:
            for dec in quest_data.get("decorators", []):
                if dec["type"] == "level_req":
                    if current_user.level < dec["value"]:
                        missing_requirements.append(f"Niveau {dec['value']} requis")
                elif dec["type"] == "npc_req":
                    if not current_user.spoken_to_npc:
                        missing_requirements.append("Parler au PNJ requis")
        
        result.append(QuestWithStatus(
            **quest_data,
            is_completed=is_completed,
            can_start=can_start,
            missing_requirements=missing_requirements
        ))
    
    return result

@router.post("/quests/{quest_id}/complete", response_model=QuestResult)
async def complete_quest(quest_id: int, current_user: User = Depends(get_current_user)):
    """Tente de compléter une quête"""
    
    # Récupérer la quête
    quest_data = db.get_quest(quest_id)
    if quest_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quête #{quest_id} introuvable"
        )
    
    # Vérifier si déjà complétée
    logger.info(f"Attempting quest {quest_id}, completed_quests: {current_user.completed_quests}")
    
    if quest_id in current_user.completed_quests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà complété cette quête"
        )
    
    # Créer la quête avec ses décorateurs
    quest_obj = QuestFactory.create_quest_from_dict(quest_data)
    
    # Vérifier les conditions
    if not quest_obj.can_start(current_user):
        missing = []
        for dec in quest_data.get("decorators", []):
            if dec["type"] == "level_req" and current_user.level < dec["value"]:
                missing.append(f"Niveau {dec['value']} requis (actuel: {current_user.level})")
            elif dec["type"] == "npc_req" and not current_user.spoken_to_npc:
                missing.append("Vous devez d'abord parler au PNJ")
        
        return QuestResult(
            success=False,
            message="Conditions non remplies",
            rewards={"missing_requirements": missing}
        )
    
    # Compléter la quête
    xp_result = current_user.add_xp(quest_data["base_xp"])
    
    # Ajouter les récompenses des décorateurs
    rewards = {
        "xp": quest_data["base_xp"],
        "leveled_up": xp_result["leveled_up"],
        "new_level": xp_result["new_level"]
    }
    
    # Vérifier si la quête nécessite le PNJ AVANT de donner les récompenses
    has_npc_requirement = any(dec["type"] == "npc_req" for dec in quest_data.get("decorators", []))
    
    for dec in quest_data.get("decorators", []):
        if dec["type"] == "money_reward":
            current_user.money += dec["value"]
            rewards["money"] = dec["value"]
        elif dec["type"] == "item_reward":
            current_user.inventory.append(dec["value"])
            rewards.setdefault("items", []).append(dec["value"])
    
    # Marquer comme complétée
    current_user.completed_quests.append(quest_id)
    logger.info(f"Quest {quest_id} completed! New completed_quests: {current_user.completed_quests}")
    
    # Reset le statut PNJ APRÈS avoir ajouté la quête aux complétées
    if has_npc_requirement:
        current_user.spoken_to_npc = False
        rewards["npc_reset"] = True
    
    # Sauvegarder (avec le reset PNJ inclus)
    db.update_user(current_user.username, current_user.to_dict())
    
    return QuestResult(
        success=True,
        message=f"Quête '{quest_data['title']}' terminée !",
        rewards=rewards,
        player_status=PlayerStatus(
            name=current_user.name,
            level=current_user.level,
            xp=current_user.xp,
            money=current_user.money,
            inventory=current_user.inventory,
            spoken_to_npc=current_user.spoken_to_npc,
            completed_quests=current_user.completed_quests
        )
    )

@router.post("/talk-npc", response_model=dict)
async def talk_to_npc(current_user: User = Depends(get_current_user)):
    """Parle au PNJ principal"""
    
    if current_user.spoken_to_npc:
        return {
            "success": False,
            "message": "Vous avez déjà parlé au PNJ principal"
        }
    
    current_user.spoken_to_npc = True
    db.update_user(current_user.username, current_user.to_dict())
    
    return {
        "success": True,
        "message": "Vous avez parlé au PNJ ! Certaines quêtes sont maintenant accessibles."
    }