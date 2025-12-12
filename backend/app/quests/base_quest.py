from app.models.quest_interfaces import IQuest

class BaseQuest(IQuest):
    """Implémentation de base d'une quête (conservée de votre code)"""
    
    def __init__(self, quest_id: int, title: str, description: str, base_xp: int, is_primary: bool = True):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.base_xp = base_xp
        self.type_label = "PRINCIPALE" if is_primary else "SECONDAIRE"

    def get_id(self) -> int:
        return self.quest_id

    def is_completed(self, player) -> bool:
        """Vérifie si la quête est dans la liste des quêtes complétées"""
        return self.quest_id in player.completed_quests

    def get_description(self) -> str:
        return f"[{self.type_label}] {self.title}: {self.description} (XP: {self.base_xp})"

    def can_start(self, player) -> bool:
        """
        ✅ CORRECTION: Retourne False si déjà complétée, True sinon
        Les décorateurs vont surcharger cette méthode pour ajouter leurs propres conditions
        """
        # Si déjà complétée, on ne peut plus la faire
        if self.is_completed(player):
            return False
        
        # Sinon, la quête de base est toujours disponible
        return True

    def complete(self, player) -> bool:
        """
        ✅ Complète la quête (applique les récompenses de base)
        Retourne True si succès, False si déjà complétée
        """
        # Ne peut pas compléter si déjà complétée
        if self.is_completed(player):
            return False
        
        # Ajouter l'XP de base
        player.add_xp(self.base_xp)
        
        # Marquer comme complétée
        if self.quest_id not in player.completed_quests:
            player.completed_quests.append(self.quest_id)
        
        return True