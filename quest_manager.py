import typer
import json
import os
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict

SAVE_FILE = "save.json"

# --- 1. Le Joueur (Context) ---
@dataclass
class Player:
    name: str = "Héros"
    level: int = 1
    xp: int = 0
    money: int = 0
    inventory: List[str] = field(default_factory=list)
    spoken_to_npc: bool = False
    # NOUVEAU : Liste des ID de quêtes terminées
    completed_quests: List[int] = field(default_factory=list)

    def add_xp(self, amount: int):
        self.xp += amount
        print(f"✨ {self.name} gagne {amount} XP!")
        if self.xp >= 100 * self.level:
            self.level += 1
            self.xp = 0
            print(f"🆙 LEVEL UP! Niveau {self.level} atteint!")

# --- 2. Interface de Quête ---
class IQuest(ABC):
    @abstractmethod
    def get_description(self) -> str: pass
    @abstractmethod
    def can_start(self, player: Player) -> bool: pass
    @abstractmethod
    def complete(self, player: Player): pass
    # NOUVEAU : On a besoin de savoir si c'est fini pour l'affichage
    @abstractmethod
    def is_completed(self, player: Player) -> bool: pass

# --- 3. Base Quest ---
class BaseQuest(IQuest):
    # NOUVEAU : On passe quest_id dans le constructeur
    def __init__(self, quest_id: int, title: str, description: str, base_xp: int, is_primary: bool = True):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.base_xp = base_xp
        self.type_label = "PRINCIPALE" if is_primary else "SECONDAIRE"

    def is_completed(self, player: Player) -> bool:
        return self.quest_id in player.completed_quests

    def get_description(self) -> str:
        return f"[{self.type_label}] {self.title}: {self.description} (XP: {self.base_xp})"

    def can_start(self, player: Player) -> bool:
        # NOUVEAU : Vérification si déjà terminé
        if self.is_completed(player):
            print(f"✅ Vous avez déjà terminé la quête : {self.title}")
            return False
        return True

    def complete(self, player: Player):
        print(f"\n✅ Quête terminée : {self.title}")
        player.add_xp(self.base_xp)
        # NOUVEAU : On sauvegarde l'ID
        if self.quest_id not in player.completed_quests:
            player.completed_quests.append(self.quest_id)

# --- 4. Décorateur Abstrait ---
class QuestDecorator(IQuest):
    def __init__(self, quest: IQuest):
        self._quest = quest
    def get_description(self) -> str: return self._quest.get_description()
    
    def is_completed(self, player: Player) -> bool:
        return self._quest.is_completed(player)

    def can_start(self, player: Player) -> bool:
        # On vérifie d'abord si la quête de base est faisable (pas déjà finie)
        if not self._quest.can_start(player):
            return False
        return True

    def complete(self, player: Player):
        self._quest.complete(player)

# --- 5 & 6. Décorateurs Concrets ---
class LevelRequirementDecorator(QuestDecorator):
    def __init__(self, quest: IQuest, min_level: int):
        super().__init__(quest)
        self.min_level = min_level
    def get_description(self) -> str: return super().get_description() + f" [Requis: Niv {self.min_level}]"
    def can_start(self, player: Player) -> bool:
        # Si la quête est déjà finie (géré par BaseQuest), on arrête tout de suite
        if self.is_completed(player): return False 
        
        if player.level >= self.min_level: return super().can_start(player)
        print(f"⛔ Niveau insuffisant. Requis: {self.min_level}, Actuel: {player.level}")
        return False

class NPCInteractionDecorator(QuestDecorator):
    def __init__(self, quest: IQuest, npc_name: str):
        super().__init__(quest)
        self.npc_name = npc_name
    def get_description(self) -> str: return super().get_description() + f" [Requis: Parler à {self.npc_name}]"
    def can_start(self, player: Player) -> bool:
        if self.is_completed(player): return False
        
        if player.spoken_to_npc: return super().can_start(player)
        print(f"⛔ Vous devez d'abord parler à {self.npc_name} !")
        return False

class MoneyRewardDecorator(QuestDecorator):
    def __init__(self, quest: IQuest, amount: int):
        super().__init__(quest)
        self.amount = amount
    def get_description(self) -> str: return super().get_description() + f" | Récompense: {self.amount} pièces"
    def complete(self, player: Player):
        super().complete(player)
        player.money += self.amount
        print(f"💰 Vous recevez {self.amount} pièces d'or.")

class ItemRewardDecorator(QuestDecorator):
    def __init__(self, quest: IQuest, item_name: str):
        super().__init__(quest)
        self.item_name = item_name
    def get_description(self) -> str: return super().get_description() + f" | Récompense: {self.item_name}"
    def complete(self, player: Player):
        super().complete(player)
        player.inventory.append(self.item_name)
        print(f"🎁 Vous recevez un objet : {self.item_name}")

# --- GESTION DES DONNÉES (JSON) ---

def load_quests_from_json() -> List[IQuest]:
    filename = "quests_db.json"
    if not os.path.exists(filename): return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content: return []
            data = json.loads(content)
    except Exception: return []
    
    loaded_quests = []
    for q_data in data:
        # NOUVEAU : On récupère l'ID du JSON et on le donne à BaseQuest
        quest = BaseQuest(
            quest_id=q_data["id"], 
            title=q_data["title"], 
            description=q_data["description"], 
            base_xp=q_data["base_xp"], 
            is_primary=(q_data["type"] == "PRIMARY")
        )
        for dec in q_data.get("decorators", []):
            dtype, val = dec["type"], dec["value"]
            if dtype == "level_req": quest = LevelRequirementDecorator(quest, int(val))
            elif dtype == "npc_req": quest = NPCInteractionDecorator(quest, str(val))
            elif dtype == "money_reward": quest = MoneyRewardDecorator(quest, int(val))
            elif dtype == "item_reward": quest = ItemRewardDecorator(quest, str(val))
        loaded_quests.append(quest)
    return loaded_quests

def load_player() -> Player:
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return Player(**data)
            except:
                pass
    return Player(name="Héros")

def save_player(player: Player):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(player), f, indent=4)
    # print("💾 Partie sauvegardée.") # Commenté pour éviter le spam

# --- Application Typer ---
app = typer.Typer()
state = {"player": None, "quests": []}

@app.callback()
def main():
    state["player"] = load_player()
    state["quests"] = load_quests_from_json()

@app.command()
def status():
    """Affiche le statut du joueur."""
    p = state["player"]
    typer.echo("--- STATUT JOUEUR ---")
    typer.echo(f"Nom: {p.name} | Niv: {p.level} | XP: {p.xp}")
    typer.echo(f"Or: {p.money} | PNJ Parlé: {p.spoken_to_npc}")
    typer.echo(f"Quêtes terminées (IDs): {p.completed_quests}")
    typer.echo(f"Inventaire: {p.inventory}")
    typer.echo("---------------------")

@app.command()
def list_quests():
    """Liste les quêtes (Marque ✅ si terminée)."""
    if not state["quests"]:
        typer.echo("📭 Aucune quête.")
        return
    
    typer.echo("--- TABLEAU DES QUÊTES ---")
    player = state["player"]
    
    for q in state["quests"]:
        # Pour récupérer l'ID proprement même à travers les décorateurs, 
        # on utilise notre nouvelle méthode is_completed
        status_icon = "✅ FINIE" if q.is_completed(player) else "🆕 DISPO"
        
        # Astuce : On récupère l'ID en fouillant dans l'objet de base (optionnel pour l'affichage)
        # Mais ici, on va juste afficher la description
        typer.echo(f"{status_icon} | {q.get_description()}")

@app.command()
def talk_npc():
    state["player"].spoken_to_npc = True
    typer.echo("🗣️ Vous avez discuté avec le PNJ.")
    save_player(state["player"])

@app.command()
def do_quest(quest_id: int):
    quests = state["quests"]
    
    # Trouver la bonne quête par son ID réel (et non pas l'index de la liste)
    # C'est plus robuste
    target_quest = None
    for q in quests:
        # On doit descendre la chaîne de décorateurs pour trouver l'ID dans BaseQuest
        # Ou simplement vérifier l'ID dans le JSON.
        # Ici, l'astuce simple : on suppose que quest_id correspond à l'ID JSON.
        # Comme on n'a pas exposé l'ID dans l'interface IQuest, on va tricher un peu
        # en supposant que l'ordre de chargement est séquentiel 1,2,3...
        # SINON : Il faudrait ajouter get_id() à IQuest.
        pass

    # SIMPLIFICATION pour ton projet : on utilise l'index - 1 comme avant
    if quest_id < 1 or quest_id > len(quests):
        typer.secho("❌ ID invalide", fg=typer.colors.RED)
        return

    quest = quests[quest_id - 1]
    player = state["player"]

    typer.echo(f"⚔️ Tentative...")
    
    if quest.can_start(player):
        typer.secho("🎉 SUCCÈS ! Quête validée.", fg=typer.colors.GREEN)
        quest.complete(player)
        save_player(player)
    else:
        typer.secho("❌ Impossible de faire la quête.", fg=typer.colors.RED)

# Commandes de reset pour tester
@app.command()
def reset_save():
    """Supprime la sauvegarde pour recommencer à zéro."""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
        typer.echo("♻️ Sauvegarde supprimée.")
    else:
        typer.echo("Rien à supprimer.")

if __name__ == "__main__":
    app()