from abc import ABC, abstractmethod
from models.player import Player

class IQuest(ABC):
    """Interface principale pour toutes les quêtes"""
    
    @abstractmethod
    def get_description(self) -> str:
        """Retourne la description complète de la quête"""
        pass
    
    @abstractmethod
    def can_start(self, player: Player) -> bool:
        """Vérifie si le joueur peut commencer la quête"""
        pass
    
    @abstractmethod
    def complete(self, player: Player):
        """Complète la quête et applique les récompenses"""
        pass
    
    @abstractmethod
    def is_completed(self, player: Player) -> bool:
        """Vérifie si la quête a déjà été terminée"""
        pass
    
    @abstractmethod
    def get_id(self) -> int:
        """Retourne l'ID unique de la quête"""
        pass