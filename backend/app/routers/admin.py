from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.dependencies import get_current_admin
from app.models.user import User
from app.schemas.quest import QuestCreate, QuestUpdate, QuestInDB
from app.database import db
import logging

# ✅ Ajouter du logging pour debug
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/quests", response_model=List[QuestInDB])
async def list_all_quests(current_user: User = Depends(get_current_admin)):
    """Liste toutes les quêtes (admin)"""
    return db.get_all_quests()

@router.post("/quests", response_model=QuestInDB, status_code=status.HTTP_201_CREATED)
async def create_quest(
    quest_data: QuestCreate,
    current_user: User = Depends(get_current_admin)
):
    """Crée une nouvelle quête"""
    
    try:
        # Générer un nouvel ID
        new_id = db.get_next_quest_id()
        logger.info(f"Creating quest with ID: {new_id}")
        
        # ✅ Convertir en dict avec mode='json' pour forcer la sérialisation
        quest_dict_raw = quest_data.model_dump(mode='json')
        logger.info(f"Quest data after dump: {quest_dict_raw}")
        
        # ✅ S'assurer que decorators est une liste de dicts simples
        decorators = []
        for dec in quest_dict_raw.get("decorators", []):
            # Vérifier le type
            logger.info(f"Processing decorator: {dec} (type: {type(dec)})")
            
            if isinstance(dec, dict):
                # Déjà un dict, on le garde
                decorators.append({
                    "type": dec["type"],
                    "value": dec["value"]
                })
            else:
                # Autre type, conversion manuelle
                decorators.append({
                    "type": str(getattr(dec, 'type', dec.get('type', ''))),
                    "value": getattr(dec, 'value', dec.get('value', None))
                })
        
        logger.info(f"Final decorators: {decorators}")
        
        # Créer la quête avec structure propre
        quest_dict = {
            "id": new_id,
            "title": str(quest_dict_raw["title"]),
            "description": str(quest_dict_raw["description"]),
            "base_xp": int(quest_dict_raw["base_xp"]),
            "type": str(quest_dict_raw["type"]),
            "decorators": decorators
        }
        
        logger.info(f"Final quest dict before save: {quest_dict}")
        
        # Sauvegarder
        db.add_quest(quest_dict)
        logger.info("Quest saved successfully")
        
        return quest_dict
        
    except Exception as e:
        logger.error(f"Error creating quest: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création: {str(e)}"
        )

@router.put("/quests/{quest_id}", response_model=QuestInDB)
async def update_quest(
    quest_id: int,
    quest_data: QuestUpdate,
    current_user: User = Depends(get_current_admin)
):
    """Modifie une quête existante"""
    
    try:
        # Vérifier que la quête existe
        existing = db.get_quest(quest_id)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quête #{quest_id} introuvable"
            )
        
        logger.info(f"Updating quest {quest_id}")
        
        # Convertir en dict
        quest_dict_raw = quest_data.model_dump(mode='json')
        logger.info(f"Update data: {quest_dict_raw}")
        
        # Traiter les decorators
        decorators = []
        for dec in quest_dict_raw.get("decorators", []):
            if isinstance(dec, dict):
                decorators.append({
                    "type": dec["type"],
                    "value": dec["value"]
                })
            else:
                decorators.append({
                    "type": str(getattr(dec, 'type', dec.get('type', ''))),
                    "value": getattr(dec, 'value', dec.get('value', None))
                })
        
        updated_quest = {
            "id": quest_id,
            "title": str(quest_dict_raw["title"]),
            "description": str(quest_dict_raw["description"]),
            "base_xp": int(quest_dict_raw["base_xp"]),
            "type": str(quest_dict_raw["type"]),
            "decorators": decorators
        }
        
        logger.info(f"Final update dict: {updated_quest}")
        
        db.update_quest(quest_id, updated_quest)
        logger.info("Quest updated successfully")
        
        return updated_quest
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating quest: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la modification: {str(e)}"
        )

@router.delete("/quests/{quest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quest(
    quest_id: int,
    current_user: User = Depends(get_current_admin)
):
    """Supprime une quête"""
    
    success = db.delete_quest(quest_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quête #{quest_id} introuvable"
        )

@router.post("/quests/fix-ids", response_model=dict)
async def fix_quest_ids(current_user: User = Depends(get_current_admin)):
    """Réattribue des IDs séquentiels à toutes les quêtes"""
    
    quests = db.get_all_quests()
    
    # Réattribuer les IDs
    for i, quest in enumerate(quests, start=1):
        quest["id"] = i
    
    db.save_quests(quests)
    
    return {
        "success": True,
        "message": f"{len(quests)} quête(s) renumérotée(s)"
    }

@router.get("/stats", response_model=dict)
async def get_stats(current_user: User = Depends(get_current_admin)):
    """Statistiques globales"""
    
    users = db.get_all_users()
    quests = db.get_all_quests()
    
    total_users = len(users)
    total_quests = len(quests)
    
    # Statistiques par utilisateur
    user_stats = []
    for username, user_data in users.items():
        if not user_data.get("is_admin", False):
            user_stats.append({
                "username": username,
                "level": user_data.get("level", 1),
                "completed_quests": len(user_data.get("completed_quests", []))
            })
    
    return {
        "total_users": total_users,
        "total_quests": total_quests,
        "users": user_stats
    }