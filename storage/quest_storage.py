import json
import os
from typing import List, Dict, Optional


class QuestStorage:
    """Gestionnaire de stockage des quêtes avec gestion d'erreurs"""
    
    def __init__(self, file_path: str = "data/quests_db.json"):
        self.file_path = file_path
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Crée le dossier data/ s'il n'existe pas"""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def load_all_quests(self) -> List[Dict]:
        """
        Charge toutes les quêtes depuis le fichier JSON
        
        Returns:
            Liste des quêtes
            
        Raises:
            ValueError: Si le fichier est corrompu
        """
        if not os.path.exists(self.file_path):
            # Créer un fichier vide si il n'existe pas
            self.save_all_quests([])
            return []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Validation du format
            if not isinstance(data, list):
                raise ValueError("Le fichier quests_db.json doit contenir une liste")
            
            # Validation de chaque quête
            for quest in data:
                self._validate_quest_structure(quest)
            
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Fichier quests_db.json corrompu: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement: {str(e)}")
    
    def _validate_quest_structure(self, quest: Dict) -> None:
        """
        Valide la structure d'une quête
        
        Raises:
            ValueError: Si la structure est invalide
        """
        required_fields = ["id", "title", "description", "base_xp", "type"]
        
        for field in required_fields:
            if field not in quest:
                raise ValueError(f"Champ requis manquant dans la quête: {field}")
        
        # Validation des types
        if not isinstance(quest["id"], int):
            raise ValueError(f"L'ID doit être un entier (quête: {quest.get('title', 'unknown')})")
        
        if not isinstance(quest["base_xp"], int):
            raise ValueError(f"L'XP doit être un entier (quête: {quest.get('title', 'unknown')})")
        
        if quest["type"] not in ["PRIMARY", "SECONDARY"]:
            raise ValueError(f"Type invalide: {quest['type']} (doit être PRIMARY ou SECONDARY)")
        
        # Validation des décorateurs
        if "decorators" in quest:
            if not isinstance(quest["decorators"], list):
                raise ValueError(f"Les décorateurs doivent être une liste (quête: {quest['title']})")
            
            for dec in quest["decorators"]:
                if not isinstance(dec, dict):
                    raise ValueError(f"Chaque décorateur doit être un dictionnaire (quête: {quest['title']})")
                
                if "type" not in dec or "value" not in dec:
                    raise ValueError(f"Décorateur incomplet (quête: {quest['title']})")
    
    def save_all_quests(self, quests: List[Dict]) -> None:
        """
        Sauvegarde toutes les quêtes dans le fichier JSON
        
        Args:
            quests: Liste des quêtes à sauvegarder
            
        Raises:
            ValueError: Si les données sont invalides
            PermissionError: Si le fichier n'est pas accessible en écriture
        """
        if not isinstance(quests, list):
            raise ValueError("Les quêtes doivent être fournies sous forme de liste")
        
        # Validation avant sauvegarde
        for quest in quests:
            self._validate_quest_structure(quest)
        
        try:
            self._ensure_data_directory()
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(quests, f, indent=2, ensure_ascii=False)
                
        except PermissionError:
            raise PermissionError(f"Impossible d'écrire dans {self.file_path}")
        except Exception as e:
            raise ValueError(f"Erreur lors de la sauvegarde: {str(e)}")
    
    def quest_exists(self, quest_id: int) -> bool:
        """
        Vérifie si une quête existe
        
        Args:
            quest_id: ID de la quête à vérifier
            
        Returns:
            True si la quête existe, False sinon
        """
        try:
            quests = self.load_all_quests()
            return any(q["id"] == quest_id for q in quests)
        except:
            return False
    
    def get_quest_by_id(self, quest_id: int) -> Optional[Dict]:
        """
        Récupère une quête par son ID
        
        Args:
            quest_id: ID de la quête
            
        Returns:
            Dictionnaire de la quête ou None si non trouvée
            
        Raises:
            ValueError: Si la quête n'existe pas
        """
        quests = self.load_all_quests()
        
        for quest in quests:
            if quest["id"] == quest_id:
                return quest
        
        raise ValueError(f"Aucune quête avec l'ID {quest_id}")
    
    def update_quest(self, quest_id: int, updated_quest: Dict) -> None:
        """
        Met à jour une quête existante
        
        Args:
            quest_id: ID de la quête à mettre à jour
            updated_quest: Nouvelles données de la quête
            
        Raises:
            ValueError: Si la quête n'existe pas ou si les données sont invalides
        """
        if not self.quest_exists(quest_id):
            raise ValueError(f"La quête #{quest_id} n'existe pas")
        
        # Validation de la structure
        self._validate_quest_structure(updated_quest)
        
        quests = self.load_all_quests()
        
        for i, quest in enumerate(quests):
            if quest["id"] == quest_id:
                quests[i] = updated_quest
                break
        
        self.save_all_quests(quests)
    
    def delete_quest(self, quest_id: int) -> bool:
        """
        Supprime une quête
        
        Args:
            quest_id: ID de la quête à supprimer
            
        Returns:
            True si la suppression a réussi
            
        Raises:
            ValueError: Si la quête n'existe pas
        """
        if not self.quest_exists(quest_id):
            raise ValueError(f"La quête #{quest_id} n'existe pas")
        
        quests = self.load_all_quests()
        quests = [q for q in quests if q["id"] != quest_id]
        self.save_all_quests(quests)
        
        return True
    
    def add_quest(self, quest: Dict) -> int:
        """
        Ajoute une nouvelle quête
        
        Args:
            quest: Dictionnaire de la quête à ajouter
            
        Returns:
            ID de la quête créée
            
        Raises:
            ValueError: Si les données sont invalides ou si l'ID existe déjà
        """
        # Validation
        self._validate_quest_structure(quest)
        
        # Vérifier que l'ID n'existe pas déjà
        if self.quest_exists(quest["id"]):
            raise ValueError(f"Une quête avec l'ID {quest['id']} existe déjà")
        
        quests = self.load_all_quests()
        quests.append(quest)
        self.save_all_quests(quests)
        
        return quest["id"]
    
    def get_next_id(self) -> int:
        """
        Récupère le prochain ID disponible
        
        Returns:
            Prochain ID disponible (max + 1)
        """
        try:
            quests = self.load_all_quests()
            if not quests:
                return 1
            return max(q["id"] for q in quests) + 1
        except:
            return 1
    
    def has_duplicate_ids(self) -> bool:
        """
        Vérifie s'il y a des IDs en double
        
        Returns:
            True si des doublons existent
        """
        try:
            quests = self.load_all_quests()
            ids = [q["id"] for q in quests]
            return len(ids) != len(set(ids))
        except:
            return False
    
    def get_duplicate_ids(self) -> List[int]:
        """
        Récupère la liste des IDs en double
        
        Returns:
            Liste des IDs qui apparaissent plusieurs fois
        """
        try:
            quests = self.load_all_quests()
            ids = [q["id"] for q in quests]
            return [id for id in set(ids) if ids.count(id) > 1]
        except:
            return []