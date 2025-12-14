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
    
    # ✅ FIX : Nettoyer l'ID de toutes les listes completed_quests
    success = db.delete_quest(quest_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quête #{quest_id} introuvable"
        )
    
    # ✅ NOUVEAU : Retirer cet ID de tous les joueurs
    users = db.get_all_users()
    for username, user_data in users.items():
        if quest_id in user_data.get("completed_quests", []):
            user_data["completed_quests"].remove(quest_id)
            db.update_user(username, user_data)
            logger.info(f"Removed quest {quest_id} from user {username}'s completed list")

@router.post("/quests/fix-ids", response_model=dict)
async def fix_quest_ids(current_user: User = Depends(get_current_admin)):
    """Réattribue des IDs séquentiels à toutes les quêtes"""
    
    quests = db.get_all_quests()
    
    # ✅ AMÉLIORATION : Mapper les anciens IDs vers les nouveaux
    id_mapping = {}
    for i, quest in enumerate(quests, start=1):
        old_id = quest["id"]
        new_id = i
        id_mapping[old_id] = new_id
        quest["id"] = new_id
    
    db.save_quests(quests)
    
    # ✅ NOUVEAU : Mettre à jour les IDs dans les completed_quests de tous les joueurs
    users = db.get_all_users()
    for username, user_data in users.items():
        old_completed = user_data.get("completed_quests", [])
        new_completed = []
        
        for old_quest_id in old_completed:
            if old_quest_id in id_mapping:
                new_completed.append(id_mapping[old_quest_id])
            # Si l'ancien ID n'existe plus dans les quêtes, on le supprime
        
        user_data["completed_quests"] = new_completed
        db.update_user(username, user_data)
        logger.info(f"Updated completed_quests for user {username}: {old_completed} -> {new_completed}")
    
    return {
        "success": True,
        "message": f"{len(quests)} quête(s) renumérotée(s)",
        "id_mapping": id_mapping
    }

@router.get("/stats", response_model=dict)
async def get_stats(current_user: User = Depends(get_current_admin)):
    """Statistiques globales avec quêtes terminées et en cours"""
    
    users = db.get_all_users()
    quests = db.get_all_quests()
    
    total_users = len(users)
    total_quests = len(quests)
    
    # ✅ CORRECTION : Calculer les quêtes terminées et en cours
    total_completed = 0
    total_in_progress = 0
    
    # Statistiques par utilisateur
    user_stats = []
    for username, user_data in users.items():
        if not user_data.get("is_admin", False):
            completed = user_data.get("completed_quests", [])
            num_completed = len(completed)
            total_completed += num_completed
            
            # En cours = total de quêtes - quêtes complétées
            in_progress = total_quests - num_completed
            total_in_progress += max(0, in_progress)
            
            user_stats.append({
                "username": username,
                "level": user_data.get("level", 1),
                "completed_quests": num_completed
            })
    
    return {
        "total_users": total_users,
        "total_quests": total_quests,
        "total_completed": total_completed,      # ✅ Nouveau
        "total_in_progress": total_in_progress,  # ✅ Nouveau
        "users": user_stats
    }

# ✅ NOUVELLE ROUTE : Nettoyer les IDs orphelins
@router.post("/clean-orphan-quest-ids", response_model=dict)
async def clean_orphan_quest_ids(current_user: User = Depends(get_current_admin)):
    """
    Nettoie les IDs de quêtes qui n'existent plus dans completed_quests
    Utile après avoir supprimé des quêtes
    """
    
    # Récupérer tous les IDs valides
    quests = db.get_all_quests()
    valid_ids = {q["id"] for q in quests}
    
    users = db.get_all_users()
    cleaned_count = 0
    
    for username, user_data in users.items():
        old_completed = user_data.get("completed_quests", [])
        new_completed = [qid for qid in old_completed if qid in valid_ids]
        
        if len(new_completed) != len(old_completed):
            removed = set(old_completed) - set(new_completed)
            user_data["completed_quests"] = new_completed
            db.update_user(username, user_data)
            cleaned_count += len(removed)
            logger.info(f"Cleaned {len(removed)} orphan IDs from {username}: {removed}")
    
    return {
        "success": True,
        "message": f"{cleaned_count} ID(s) orphelin(s) nettoyé(s)",
        "valid_quest_ids": list(valid_ids)
    }