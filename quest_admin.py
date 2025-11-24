import typer
import json
import os
from typing import List, Dict, Any
from enum import Enum

app = typer.Typer()
DB_FILE = "quests_db.json"

# --- CONFIGURATION DES TYPES ---
class DecoratorType(str, Enum):
    LEVEL_REQ = "level_req"
    NPC_REQ = "npc_req"
    MONEY_REWARD = "money_reward"
    ITEM_REWARD = "item_reward"

# --- GESTION DB ---
def load_db() -> List[Dict[str, Any]]:
    if not os.path.exists(DB_FILE): return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except json.JSONDecodeError:
        return []

def save_db(data: List[Dict[str, Any]]):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- OUTILS D'AFFICHAGE ---
def print_quest_details(q: Dict):
    """Affiche proprement l'état actuel de la quête."""
    typer.secho(f"\n--- ÉTAT ACTUEL DE LA QUÊTE (ID: {q['id']}) ---", fg=typer.colors.CYAN)
    typer.echo(f"1. Titre       : {q['title']}")
    typer.echo(f"2. Description : {q['description']}")
    typer.echo(f"3. XP Base     : {q['base_xp']}")
    typer.echo(f"4. Type        : {q['type']}")
    typer.echo("5. Décorateurs (Conditions/Récompenses) :")
    
    if not q['decorators']:
        typer.secho("   (Aucun)", fg=typer.colors.BRIGHT_BLACK)
    else:
        for idx, dec in enumerate(q['decorators']):
            typer.echo(f"   [{idx}] {dec['type']} -> {dec['value']}")
    typer.echo("-" * 40)

# --- SOUS-FONCTIONS DE MODIFICATION ---
def manage_decorators(quest: Dict):
    """Sous-menu pour ajouter/supprimer des décorateurs."""
    while True:
        typer.secho("\n--- GESTION DES DÉCORATEURS ---", fg=typer.colors.MAGENTA)
        typer.echo("L. Lister")
        typer.echo("A. Ajouter un décorateur")
        typer.echo("S. Supprimer un décorateur")
        typer.echo("R. Retour au menu principal")
        
        choice = typer.prompt("Action").upper()

        if choice == "R":
            break
        
        elif choice == "L":
            print_quest_details(quest)

        elif choice == "A":
            typer.echo("\nTypes disponibles :")
            typer.echo("1. Condition : Niveau requis")
            typer.echo("2. Condition : PNJ requis")
            typer.echo("3. Récompense : Argent")
            typer.echo("4. Récompense : Objet")
            
            sub_c = typer.prompt("Votre choix", type=int)
            new_dec = {}
            
            if sub_c == 1:
                val = typer.prompt("Niveau", type=int)
                new_dec = {"type": DecoratorType.LEVEL_REQ, "value": val}
            elif sub_c == 2:
                val = typer.prompt("Nom PNJ")
                new_dec = {"type": DecoratorType.NPC_REQ, "value": val}
            elif sub_c == 3:
                val = typer.prompt("Montant", type=int)
                new_dec = {"type": DecoratorType.MONEY_REWARD, "value": val}
            elif sub_c == 4:
                val = typer.prompt("Nom Objet")
                new_dec = {"type": DecoratorType.ITEM_REWARD, "value": val}
            
            if new_dec:
                quest["decorators"].append(new_dec)
                typer.secho("➕ Décorateur ajouté !", fg=typer.colors.GREEN)

        elif choice == "S":
            if not quest["decorators"]:
                typer.secho("Rien à supprimer.", fg=typer.colors.RED)
                continue
            
            # Afficher la liste avec index
            for idx, dec in enumerate(quest["decorators"]):
                typer.echo(f"{idx}. {dec['type']} ({dec['value']})")
            
            idx_to_del = typer.prompt("Index à supprimer", type=int)
            if 0 <= idx_to_del < len(quest["decorators"]):
                removed = quest["decorators"].pop(idx_to_del)
                typer.secho(f"🗑️ Supprimé : {removed['type']}", fg=typer.colors.YELLOW)
            else:
                typer.secho("Index invalide.", fg=typer.colors.RED)

# --- COMMANDES PRINCIPALES ---

@app.command()
def create():
    """Crée une nouvelle quête."""
    typer.secho("--- CRÉATION ---", bold=True)
    title = typer.prompt("Titre")
    desc = typer.prompt("Description")
    xp = typer.prompt("XP", type=int)
    is_prim = typer.confirm("Quête Principale ?", default=True)
    
    db = load_db()
    new_id = 1 if not db else max(q["id"] for q in db) + 1
    
    new_quest = {
        "id": new_id,
        "title": title,
        "description": desc,
        "base_xp": xp,
        "type": "PRIMARY" if is_prim else "SECONDARY",
        "decorators": []
    }
    
    # On propose d'ajouter des décorateurs tout de suite
    if typer.confirm("Voulez-vous configurer les conditions/récompenses maintenant ?", default=True):
        manage_decorators(new_quest)
    
    db.append(new_quest)
    save_db(db)
    typer.secho(f"✅ Quête '{title}' créée (ID: {new_id})", fg=typer.colors.GREEN)

@app.command()
def modify(quest_id: int):
    """Menu complet pour modifier une quête existante."""
    db = load_db()
    # Recherche de la quête
    quest = next((q for q in db if q["id"] == quest_id), None)
    
    if not quest:
        typer.secho(f"❌ ID {quest_id} introuvable.", fg=typer.colors.RED)
        return

    while True:
        print_quest_details(quest)
        typer.secho("\nMENU MODIFICATION", bold=True)
        typer.echo("1. Modifier le Titre")
        typer.echo("2. Modifier la Description")
        typer.echo("3. Modifier l'XP de base")
        typer.echo("4. Changer le Type (Principal/Secondaire)")
        typer.echo("5. Gérer les Décorateurs (Ajout/Retrait)")
        typer.echo("6. Sauvegarder et Quitter")
        typer.echo("0. Annuler (Sans sauvegarder)")

        choice = typer.prompt("Votre choix", type=int)

        if choice == 1:
            quest["title"] = typer.prompt("Nouveau Titre", default=quest["title"])
        elif choice == 2:
            quest["description"] = typer.prompt("Nouvelle Description", default=quest["description"])
        elif choice == 3:
            quest["base_xp"] = typer.prompt("Nouveau XP", type=int, default=quest["base_xp"])
        elif choice == 4:
            is_prim = typer.confirm("Est-ce une quête PRINCIPALE ?", default=(quest["type"] == "PRIMARY"))
            quest["type"] = "PRIMARY" if is_prim else "SECONDARY"
        elif choice == 5:
            manage_decorators(quest)
        elif choice == 6:
            save_db(db)
            typer.secho("💾 Modifications enregistrées !", fg=typer.colors.GREEN)
            break
        elif choice == 0:
            typer.secho("Annulation...", fg=typer.colors.YELLOW)
            break
        else:
            typer.secho("Choix invalide.", fg=typer.colors.RED)

@app.command()
def list():
    """Liste simple des quêtes."""
    db = load_db()
    typer.echo(f"{'ID':<4} | {'TITRE':<20} | {'XP':<5}")
    typer.echo("-" * 40)
    for q in db:
        typer.echo(f"{q['id']:<4} | {q['title']:<20} | {q['base_xp']:<5}")

@app.command()
def delete(quest_id: int):
    """Supprime une quête."""
    db = load_db()
    new_db = [q for q in db if q['id'] != quest_id]
    if len(db) == len(new_db):
        typer.secho("❌ ID introuvable.", fg=typer.colors.RED)
    else:
        save_db(new_db)
        typer.secho("🗑️ Quête supprimée.", fg=typer.colors.GREEN)

@app.command()
def fix_ids():
    """🔧 Répare les doublons en réattribuant de nouveaux IDs à tout le monde."""
    db = load_db()
    if not db:
        typer.echo("Base de données vide.")
        return

    typer.echo("🛠️ Réparation des IDs en cours...")
    
    # On réattribue un ID unique basé sur la position dans la liste (1, 2, 3...)
    for index, quest in enumerate(db):
        old_id = quest["id"]
        new_id = index + 1
        quest["id"] = new_id
        # On affiche le changement si l'ID change
        if old_id != new_id:
            print(f"  - Quête '{quest['title']}': ID {old_id} -> {new_id}")

    save_db(db)
    typer.secho("✅ Tous les IDs sont maintenant uniques et séquentiels !", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()