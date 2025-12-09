import json
import os
from typing import Optional
from models.player import Player


class PlayerStorage:
    """Gestionnaire de stockage de la sauvegarde du joueur"""
    
    def __init__(self, file_path: str = "data/save.json"):
        self.file_path = file_path
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Crée le dossier data/ s'il n'existe pas"""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def _get_default_player(self) -> Player:
        """
        Crée un joueur par défaut
        
        Returns:
            Instance de Player avec valeurs par défaut
        """
        return Player(
            name="Héros",
            level=1,
            xp=0,
            money=100,
            inventory=[],
            spoken_to_npc=False,
            completed_quests=[]
        )
    
    def _validate_player_data(self, data: dict) -> None:
        """
        Valide les données d'un joueur
        
        Args:
            data: Dictionnaire contenant les données du joueur
            
        Raises:
            ValueError: Si les données sont invalides
        """
        required_fields = ["name", "level", "xp", "money", "inventory", "spoken_to_npc", "completed_quests"]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Champ requis manquant: {field}")
        
        # Validation des types
        if not isinstance(data["name"], str) or not data["name"].strip():
            raise ValueError("Le nom doit être une chaîne non vide")
        
        if not isinstance(data["level"], int) or data["level"] < 1:
            raise ValueError("Le niveau doit être un entier positif")
        
        if not isinstance(data["xp"], int) or data["xp"] < 0:
            raise ValueError("L'XP doit être un entier positif ou nul")
        
        if not isinstance(data["money"], int) or data["money"] < 0:
            raise ValueError("L'argent doit être un entier positif ou nul")
        
        if not isinstance(data["inventory"], list):
            raise ValueError("L'inventaire doit être une liste")
        
        if not isinstance(data["spoken_to_npc"], bool):
            raise ValueError("spoken_to_npc doit être un booléen")
        
        if not isinstance(data["completed_quests"], list):
            raise ValueError("completed_quests doit être une liste")
        
        # Validation des éléments de l'inventaire
        for item in data["inventory"]:
            if not isinstance(item, str):
                raise ValueError("Chaque objet de l'inventaire doit être une chaîne")
        
        # Validation des IDs de quêtes complétées
        for quest_id in data["completed_quests"]:
            if not isinstance(quest_id, int):
                raise ValueError("Chaque ID de quête doit être un entier")
    
    def load(self) -> Player:
        """
        Charge la sauvegarde du joueur
        
        Returns:
            Instance de Player
            
        Raises:
            ValueError: Si le fichier est corrompu
        """
        if not os.path.exists(self.file_path):
            # Créer un joueur par défaut si aucune sauvegarde
            default_player = self._get_default_player()
            self.save(default_player)
            return default_player
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validation des données
            self._validate_player_data(data)
            
            # Création du joueur
            return Player(
                name=data["name"],
                level=data["level"],
                xp=data["xp"],
                money=data["money"],
                inventory=data["inventory"],
                spoken_to_npc=data["spoken_to_npc"],
                completed_quests=data["completed_quests"]
            )
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Fichier de sauvegarde corrompu: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement de la sauvegarde: {str(e)}")
    
    def save(self, player: Player) -> None:
        """
        Sauvegarde les données du joueur
        
        Args:
            player: Instance de Player à sauvegarder
            
        Raises:
            ValueError: Si les données sont invalides
            PermissionError: Si le fichier n'est pas accessible en écriture
        """
        if not isinstance(player, Player):
            raise ValueError("Le paramètre doit être une instance de Player")
        
        # Conversion en dictionnaire
        player_data = {
            "name": player.name,
            "level": player.level,
            "xp": player.xp,
            "money": player.money,
            "inventory": player.inventory,
            "spoken_to_npc": player.spoken_to_npc,
            "completed_quests": player.completed_quests
        }
        
        # Validation avant sauvegarde
        self._validate_player_data(player_data)
        
        try:
            self._ensure_data_directory()
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(player_data, f, indent=2, ensure_ascii=False)
                
        except PermissionError:
            raise PermissionError(f"Impossible d'écrire dans {self.file_path}")
        except Exception as e:
            raise ValueError(f"Erreur lors de la sauvegarde: {str(e)}")
    
    def exists(self) -> bool:
        """
        Vérifie si un fichier de sauvegarde existe
        
        Returns:
            True si le fichier existe
        """
        return os.path.exists(self.file_path)
    
    def reset(self) -> Player:
        """
        Réinitialise la sauvegarde avec un joueur par défaut
        
        Returns:
            Nouveau joueur par défaut
        """
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        
        default_player = self._get_default_player()
        self.save(default_player)
        return default_player
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """
        Crée une sauvegarde de backup
        
        Args:
            backup_path: Chemin du fichier de backup (optionnel)
            
        Returns:
            Chemin du fichier de backup créé
            
        Raises:
            FileNotFoundError: Si aucune sauvegarde à backup
        """
        if not self.exists():
            raise FileNotFoundError("Aucune sauvegarde à backup")
        
        if backup_path is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/save_backup_{timestamp}.json"
        
        # Copier le fichier
        with open(self.file_path, 'r', encoding='utf-8') as source:
            data = source.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dest:
            dest.write(data)
        
        return backup_path
    
    def restore(self, backup_path: str) -> Player:
        """
        Restaure une sauvegarde depuis un backup
        
        Args:
            backup_path: Chemin du fichier de backup
            
        Returns:
            Joueur restauré
            
        Raises:
            FileNotFoundError: Si le backup n'existe pas
            ValueError: Si le backup est corrompu
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Fichier de backup introuvable: {backup_path}")
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validation
            self._validate_player_data(data)
            
            # Sauvegarde
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return self.load()
            
        except json.JSONDecodeError:
            raise ValueError(f"Le fichier de backup est corrompu: {backup_path}")
        except Exception as e:
            raise ValueError(f"Erreur lors de la restauration: {str(e)}")