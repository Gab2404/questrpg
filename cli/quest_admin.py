# ================================
# cli/__init__.py
# ================================
"""
Module CLI pour l'administration et le jeu
"""
# Pas d'imports nécessaires ici, les modules sont utilisés directement


# ================================
# cli/quest_admin.py
# ================================
import typer
from typing import Dict
from enum import Enum
from storage.quest_storage import load_quests_db, save_quests_db

app = typer.Typer()

class DecoratorType(str, Enum):
    LEVEL_REQ = "level_req"
    NPC_REQ = "npc_req"
    MONEY_REWARD = "money_reward"
    ITEM_REWARD = "item_reward"

def print_quest_details(q: Dict):
    """Affiche proprement l'état actuel de la quête"""
    typer.secho(f"\n╔═══════════════════════════════════════════╗", fg=typer.colors.CYAN)
    typer.secho(f"║  ÉTAT ACTUEL DE LA QUÊTE (ID: {q['id']})       ║", fg=typer.colors.CYAN)
    typer.secho(f"╚═══════════════════════════════════════════╝", fg=typer.colors.CYAN)
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

def manage_decorators(quest: Dict):
    """Sous-menu pour ajouter/supprimer des décorateurs"""
    while True:
        typer.secho("\n╔═══════════════════════════════╗", fg=typer.colors.MAGENTA)
        typer.secho("║   GESTION DES DÉCORATEURS     ║", fg=typer.colors.MAGENTA)
        typer.secho("╚═══════════════════════════════╝", fg=typer.colors.MAGENTA)
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
            typer.echo("\n📋 Types disponibles :")
            typer.echo("1. Condition : Niveau requis")
            typer.echo("2. Condition : PNJ requis")
            typer.echo("3. Récompense : Argent")
            typer.echo("4. Récompense : Objet")
            
            sub_c = typer.prompt("Votre choix", type=int)
            new_dec = {}
            
            if sub_c == 1:
                val = typer.prompt("Niveau minimum", type=int)
                new_dec = {"type": DecoratorType.LEVEL_REQ, "value": val}
            elif sub_c == 2:
                val = typer.prompt("Nom du PNJ")
                new_dec = {"type": DecoratorType.NPC_REQ, "value": val}
            elif sub_c == 3:
                val = typer.prompt("Montant en pièces", type=int)
                new_dec = {"type": DecoratorType.MONEY_REWARD, "value": val}
            elif sub_c == 4:
                val = typer.prompt("Nom de l'objet")
                new_dec = {"type": DecoratorType.ITEM_REWARD, "value": val}
            else:
                typer.secho("❌ Choix invalide.", fg=typer.colors.RED)
                continue
            
            if new_dec:
                quest["decorators"].append(new_dec)
                typer.secho("➕ Décorateur ajouté !", fg=typer.colors.GREEN)

        elif choice == "S":
            if not quest["decorators"]:
                typer.secho("⚠️  Aucun décorateur à supprimer.", fg=typer.colors.YELLOW)
                continue
            
            for idx, dec in enumerate(quest["decorators"]):
                typer.echo(f"{idx}. {dec['type']} ({dec['value']})")
            
            idx_to_del = typer.prompt("Index à supprimer", type=int)
            if 0 <= idx_to_del < len(quest["decorators"]):
                removed = quest["decorators"].pop(idx_to_del)
                typer.secho(f"🗑️  Supprimé : {removed['type']}", fg=typer.colors.YELLOW)
            else:
                typer.secho("❌ Index invalide.", fg=typer.colors.RED)

@app.command()
def create():
    """Crée une nouvelle quête de manière interactive"""
    typer.secho("\n╔═══════════════════════════════╗", bold=True, fg=typer.colors.GREEN)
    typer.secho("║    CRÉATION D'UNE QUÊTE       ║", bold=True, fg=typer.colors.GREEN)
    typer.secho("╚═══════════════════════════════╝", bold=True, fg=typer.colors.GREEN)
    
    title = typer.prompt("📝 Titre de la quête")
    desc = typer.prompt("📖 Description")
    xp = typer.prompt("⭐ XP de base", type=int)
    is_prim = typer.confirm("🎯 Quête Principale ?", default=True)
    
    db = load_quests_db()
    new_id = 1 if not db else max(q["id"] for q in db) + 1
    
    new_quest = {
        "id": new_id,
        "title": title,
        "description": desc,
        "base_xp": xp,
        "type": "PRIMARY" if is_prim else "SECONDARY",
        "decorators": []
    }
    
    if typer.confirm("⚙️  Voulez-vous configurer les conditions/récompenses maintenant ?", default=True):
        manage_decorators(new_quest)
    
    db.append(new_quest)
    save_quests_db(db)
    typer.secho(f"✅ Quête '{title}' créée avec succès (ID: {new_id})", fg=typer.colors.GREEN)

@app.command()
def modify(quest_id: int):
    """
    Menu complet pour modifier une quête existante
    
    Args:
        quest_id: ID de la quête à modifier
    """
    db = load_quests_db()
    quest = next((q for q in db if q["id"] == quest_id), None)
    
    if not quest:
        typer.secho(f"❌ Quête avec l'ID {quest_id} introuvable.", fg=typer.colors.RED)
        return

    while True:
        print_quest_details(quest)
        typer.secho("\n╔═══════════════════════════════╗", bold=True)
        typer.secho("║     MENU MODIFICATION         ║", bold=True)
        typer.secho("╚═══════════════════════════════╝", bold=True)
        typer.echo("1. Modifier le Titre")
        typer.echo("2. Modifier la Description")
        typer.echo("3. Modifier l'XP de base")
        typer.echo("4. Changer le Type (Principal/Secondaire)")
        typer.echo("5. Gérer les Décorateurs (Ajout/Retrait)")
        typer.echo("6. 💾 Sauvegarder et Quitter")
        typer.echo("0. ❌ Annuler (Sans sauvegarder)")

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
            save_quests_db(db)
            typer.secho("💾 Modifications enregistrées avec succès !", fg=typer.colors.GREEN)
            break
        elif choice == 0:
            typer.secho("⚠️  Annulation... Aucune modification sauvegardée.", fg=typer.colors.YELLOW)
            break
        else:
            typer.secho("❌ Choix invalide.", fg=typer.colors.RED)

@app.command()
def list():
    """Liste toutes les quêtes sous forme de tableau"""
    db = load_quests_db()
    
    if not db:
        typer.secho("🔭 Aucune quête dans la base de données.", fg=typer.colors.YELLOW)
        return
    
    typer.echo("\n╔════════════════════════════════════════════════╗")
    typer.echo("║          LISTE DES QUÊTES                      ║")
    typer.echo("╚════════════════════════════════════════════════╝")
    typer.echo(f"{'ID':<4} | {'TITRE':<25} | {'TYPE':<10} | {'XP':<5}")
    typer.echo("-" * 55)
    
    for q in db:
        type_label = "PRINCIPALE" if q['type'] == "PRIMARY" else "SECONDAIRE"
        typer.echo(f"{q['id']:<4} | {q['title']:<25} | {type_label:<10} | {q['base_xp']:<5}")

@app.command()
def delete(quest_id: int):
    """
    Supprime définitivement une quête
    
    Args:
        quest_id: ID de la quête à supprimer
    """
    db = load_quests_db()
    new_db = [q for q in db if q['id'] != quest_id]
    
    if len(db) == len(new_db):
        typer.secho(f"❌ Quête avec l'ID {quest_id} introuvable.", fg=typer.colors.RED)
    else:
        save_quests_db(new_db)
        typer.secho(f"🗑️  Quête {quest_id} supprimée avec succès.", fg=typer.colors.GREEN)

@app.command()
def fix_ids():
    """🔧 Répare les doublons en réattribuant de nouveaux IDs séquentiels"""
    db = load_quests_db()
    
    if not db:
        typer.secho("ℹ️  Base de données vide.", fg=typer.colors.BLUE)
        return

    typer.echo("🛠️  Réparation des IDs en cours...")
    
    for index, quest in enumerate(db, start=1):
        old_id = quest["id"]
        new_id = index
        quest["id"] = new_id
        
        if old_id != new_id:
            typer.echo(f"  • Quête '{quest['title']}': ID {old_id} → {new_id}")

    save_quests_db(db)
    typer.secho("✅ Tous les IDs sont maintenant uniques et séquentiels !", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()