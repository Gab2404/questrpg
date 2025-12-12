from abc import ABC, abstractmethod

class IQuest(ABC):
    """Interface principale pour toutes les quêtes (conservée de votre code)"""
    
    @abstractmethod
    def get_description(self) -> str:
        """Retourne la description complète de la quête"""
        pass
    
    @abstractmethod
    def can_start(self, player) -> bool:
        """Vérifie si le joueur peut commencer la quête"""
        pass
    
    @abstractmethod
    def complete(self, player) -> bool:
        """Complète la quête et applique les récompenses"""
        pass
    
    @abstractmethod
    def is_completed(self, player) -> bool:
        """Vérifie si la quête a déjà été terminée"""
        pass
    
    @abstractmethod
    def get_id(self) -> int:
        """Retourne l'ID unique de la quête"""
        pass