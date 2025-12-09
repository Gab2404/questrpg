import typer
import json
from typing import Dict, Optional
from functools import wraps
from storage.quest_storage import QuestStorage
from storage.player_storage import PlayerStorage

app = typer.Typer(help="Interface d'administration des quêtes")

def safe_command(func):
    """Décorateur pour gérer les erreurs de manière élégante"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except typer.Exit:
            raise  # Laisser passer les exits volontaires
        except FileNotFoundError as e:
            typer.secho(f"❌ Fichier introuvable: {e}", fg=typer.colors.RED)
            raise typer.Exit(1)
        except PermissionError:
            typer.secho("❌ Permission refusée. Vérifiez les droits d'accès", fg=typer.colors.RED)
            raise typer.Exit(1)
        except json.JSONDecodeError:
            typer.secho("❌ Fichier JSON corrompu.", fg=typer.colors.RED)
            typer.secho("💡 Utilisez 'diagnose' pour plus d'informations", fg=typer.colors.YELLOW)
            raise typer.Exit(1)
        except Exception as e:
            typer.secho(f"❌ Erreur inattendue: {str(e)}", fg=typer.colors.RED)
            typer.secho("💡 Utilisez --help pour l'aide", fg=typer.colors.YELLOW)
            raise typer.Exit(1)
    return wrapper


def validate_quest_id(quest_id: int) -> int:
    """Valide qu'un ID de quête est correct"""
    if quest_id <= 0:
        typer.secho("❌ L'ID doit être un nombre positif", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    storage = QuestStorage()
    
    if not storage.quest_exists(quest_id):
        typer.secho(f"❌ Aucune quête avec l'ID {quest_id}", fg=typer.colors.RED)
        typer.secho("💡 Utilisez 'list' pour voir les quêtes disponibles", fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    
    return quest_id

@app.command()
@safe_command
def list():
    """Liste toutes les quêtes disponibles"""
    storage = QuestStorage()
    quests = storage.load_all_quests()
    
    if not quests:
        typer.secho("ℹ️  Aucune quête disponible", fg=typer.colors.YELLOW)
        typer.secho("💡 Utilisez 'create' pour créer une nouvelle quête", fg=typer.colors.CYAN)
        return
    
    typer.secho("\n╔════╦══════════════════════════╦═══════════╦═════════╗", fg=typer.colors.CYAN)
    typer.secho("║ ID ║ Titre                    ║ Type      ║ XP Base ║", fg=typer.colors.CYAN)
    typer.secho("╠════╬══════════════════════════╬═══════════╬═════════╣", fg=typer.colors.CYAN)
    
    for quest in quests:
        quest_id = str(quest["id"]).center(2)
        title = quest["title"][:24].ljust(24)
        quest_type = quest["type"][:9].ljust(9)
        xp = str(quest["base_xp"]).center(7)
        
        typer.secho(f"║ {quest_id} ║ {title} ║ {quest_type} ║ {xp} ║", fg=typer.colors.WHITE)
    
    typer.secho("╚════╩══════════════════════════╩═══════════╩═════════╝\n", fg=typer.colors.CYAN)


@app.command()
@safe_command
def create():
    """Crée une nouvelle quête de manière interactive"""
    storage = QuestStorage()
    
    typer.secho("\n🎯 CRÉATION D'UNE NOUVELLE QUÊTE\n", fg=typer.colors.CYAN, bold=True)
    
    # Informations de base
    title = typer.prompt("📝 Titre de la quête")
    if not title.strip():
        typer.secho("❌ Le titre ne peut pas être vide", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    description = typer.prompt("📖 Description")
    if not description.strip():
        typer.secho("❌ La description ne peut pas être vide", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    # XP avec validation
    while True:
        try:
            base_xp = typer.prompt("⭐ XP de base", type=int)
            if base_xp <= 0:
                typer.secho("⚠️  L'XP doit être supérieur à 0", fg=typer.colors.YELLOW)
                continue
            if base_xp > 10000:
                confirm = typer.confirm(f"⚠️  {base_xp} XP est très élevé. Confirmer ?")
                if not confirm:
                    continue
            break
        except ValueError:
            typer.secho("❌ Veuillez entrer un nombre valide", fg=typer.colors.RED)
    
    # Type de quête
    is_primary = typer.confirm("🎯 Quête Principale ?", default=True)
    quest_type = "PRIMARY" if is_primary else "SECONDARY"
    
    # Génération de l'ID
    quests = storage.load_all_quests()
    new_id = max([q["id"] for q in quests], default=0) + 1
    
    # Création de la quête
    new_quest = {
        "id": new_id,
        "title": title,
        "description": description,
        "base_xp": base_xp,
        "type": quest_type,
        "decorators": []
    }
    
    # Configuration des décorateurs
    configure = typer.confirm("\n⚙️  Voulez-vous configurer les conditions/récompenses maintenant ?", default=True)
    
    if configure:
        new_quest["decorators"] = configure_decorators([])
    
    # Sauvegarde
    quests.append(new_quest)
    storage.save_all_quests(quests)
    
    typer.secho(f"\n✅ Quête #{new_id} créée avec succès !", fg=typer.colors.GREEN, bold=True)
    typer.secho(f"   Titre: {title}", fg=typer.colors.CYAN)
    typer.secho(f"   Type: {quest_type}", fg=typer.colors.CYAN)
    typer.secho(f"   XP: {base_xp}", fg=typer.colors.CYAN)
    typer.secho(f"   Décorateurs: {len(new_quest['decorators'])}", fg=typer.colors.CYAN)


@app.command()
@safe_command
def modify(quest_id: int):
    """Modifie une quête existante"""
    quest_id = validate_quest_id(quest_id)
    
    storage = QuestStorage()
    quest = storage.get_quest_by_id(quest_id)
    
    while True:
        typer.clear()
        typer.secho(f"\n╔════════════════════════════════════════════════════════════╗", fg=typer.colors.CYAN)
        typer.secho(f"║          MODIFICATION DE LA QUÊTE #{quest_id:02d}                       ║", fg=typer.colors.CYAN)
        typer.secho(f"╠════════════════════════════════════════════════════════════╣", fg=typer.colors.CYAN)
        typer.secho(f"║ Titre       : {quest['title'][:44].ljust(44)} ║", fg=typer.colors.WHITE)
        typer.secho(f"║ Description : {quest['description'][:44].ljust(44)} ║", fg=typer.colors.WHITE)
        typer.secho(f"║ XP Base     : {str(quest['base_xp']).ljust(44)} ║", fg=typer.colors.WHITE)
        typer.secho(f"║ Type        : {quest['type'].ljust(44)} ║", fg=typer.colors.WHITE)
        typer.secho(f"╠════════════════════════════════════════════════════════════╣", fg=typer.colors.CYAN)
        
        if quest.get("decorators"):
            typer.secho(f"║ Décorateurs actuels:                                       ║", fg=typer.colors.CYAN)
            for i, dec in enumerate(quest["decorators"], 1):
                dec_str = f"   [{i}] {dec['type']}: {dec['value']}"[:56]
                typer.secho(f"║ {dec_str.ljust(58)} ║", fg=typer.colors.YELLOW)
        else:
            typer.secho(f"║ Aucun décorateur                                           ║", fg=typer.colors.YELLOW)
        
        typer.secho(f"╠════════════════════════════════════════════════════════════╣", fg=typer.colors.CYAN)
        typer.secho(f"║ [1] Modifier le titre                                      ║", fg=typer.colors.WHITE)
        typer.secho(f"║ [2] Modifier la description                                ║", fg=typer.colors.WHITE)
        typer.secho(f"║ [3] Modifier l'XP de base                                  ║", fg=typer.colors.WHITE)
        typer.secho(f"║ [4] Changer le type                                        ║", fg=typer.colors.WHITE)
        typer.secho(f"║ [5] Gérer les décorateurs                                  ║", fg=typer.colors.WHITE)
        typer.secho(f"║ [S] Sauvegarder et quitter                                 ║", fg=typer.colors.GREEN)
        typer.secho(f"║ [Q] Annuler                                                ║", fg=typer.colors.RED)
        typer.secho(f"╚════════════════════════════════════════════════════════════╝\n", fg=typer.colors.CYAN)
        
        choice = typer.prompt("Votre choix").strip().upper()
        
        if choice == "1":
            new_title = typer.prompt("Nouveau titre", default=quest["title"])
            if new_title.strip():
                quest["title"] = new_title
                typer.secho("✅ Titre modifié", fg=typer.colors.GREEN)
            else:
                typer.secho("❌ Le titre ne peut pas être vide", fg=typer.colors.RED)
            typer.pause()
            
        elif choice == "2":
            new_desc = typer.prompt("Nouvelle description", default=quest["description"])
            if new_desc.strip():
                quest["description"] = new_desc
                typer.secho("✅ Description modifiée", fg=typer.colors.GREEN)
            else:
                typer.secho("❌ La description ne peut pas être vide", fg=typer.colors.RED)
            typer.pause()
            
        elif choice == "3":
            try:
                new_xp = typer.prompt("Nouvelle valeur d'XP", type=int, default=quest["base_xp"])
                if new_xp <= 0:
                    typer.secho("❌ L'XP doit être supérieur à 0", fg=typer.colors.RED)
                else:
                    quest["base_xp"] = new_xp
                    typer.secho("✅ XP modifié", fg=typer.colors.GREEN)
            except ValueError:
                typer.secho("❌ Valeur invalide", fg=typer.colors.RED)
            typer.pause()
            
        elif choice == "4":
            current = "Principale" if quest["type"] == "PRIMARY" else "Secondaire"
            typer.secho(f"Type actuel: {current}", fg=typer.colors.YELLOW)
            is_primary = typer.confirm("Quête Principale ?", default=(quest["type"] == "PRIMARY"))
            quest["type"] = "PRIMARY" if is_primary else "SECONDARY"
            typer.secho("✅ Type modifié", fg=typer.colors.GREEN)
            typer.pause()
            
        elif choice == "5":
            quest["decorators"] = configure_decorators(quest.get("decorators", []))
            
        elif choice == "S":
            storage.update_quest(quest_id, quest)
            typer.secho("\n✅ Modifications sauvegardées !", fg=typer.colors.GREEN, bold=True)
            break
            
        elif choice == "Q":
            confirm = typer.confirm("⚠️  Abandonner les modifications ?")
            if confirm:
                typer.secho("❌ Modifications annulées", fg=typer.colors.YELLOW)
                break
        else:
            typer.secho("❌ Choix invalide", fg=typer.colors.RED)
            typer.pause()


@app.command()
@safe_command
def delete(quest_id: int):
    """Supprime une quête existante"""
    quest_id = validate_quest_id(quest_id)
    
    storage = QuestStorage()
    quest = storage.get_quest_by_id(quest_id)
    
    # Afficher les détails
    typer.secho(f"\n⚠️  SUPPRESSION DE LA QUÊTE #{quest_id}", fg=typer.colors.RED, bold=True)
    typer.secho(f"   Titre: {quest['title']}", fg=typer.colors.YELLOW)
    typer.secho(f"   Type: {quest['type']}", fg=typer.colors.YELLOW)
    
    # Confirmation
    confirm = typer.confirm(f"\n⚠️  Voulez-vous vraiment supprimer cette quête ?", default=False)
    
    if not confirm:
        typer.secho("❌ Suppression annulée", fg=typer.colors.YELLOW)
        raise typer.Exit(0)
    
    storage.delete_quest(quest_id)
    typer.secho(f"\n✅ Quête #{quest_id} supprimée avec succès", fg=typer.colors.GREEN)


@app.command()
@safe_command
def fix_ids():
    """Répare les IDs en double et réattribue des IDs séquentiels"""
    storage = QuestStorage()
    quests = storage.load_all_quests()
    
    if not quests:
        typer.secho("ℹ️  Aucune quête à corriger", fg=typer.colors.YELLOW)
        return
    
    # Détecter les doublons
    ids = [q["id"] for q in quests]
    duplicates = [id for id in set(ids) if ids.count(id) > 1]
    
    if not duplicates:
        typer.secho("✅ Aucun doublon détecté", fg=typer.colors.GREEN)
        return
    
    typer.secho(f"⚠️  {len(duplicates)} ID(s) en double détecté(s): {duplicates}", fg=typer.colors.YELLOW)
    
    confirm = typer.confirm("Réattribuer des IDs séquentiels à toutes les quêtes ?")
    
    if not confirm:
        typer.secho("❌ Opération annulée", fg=typer.colors.YELLOW)
        return
    
    # Réattribution
    for i, quest in enumerate(quests, start=1):
        quest["id"] = i
    
    storage.save_all_quests(quests)
    typer.secho(f"✅ {len(quests)} quête(s) renumérotée(s) (1 à {len(quests)})", fg=typer.colors.GREEN)


@app.command()
@safe_command
def diagnose():
    """Diagnostic complet du système"""
    typer.secho("\n🔍 DIAGNOSTIC DU SYSTÈME\n", fg=typer.colors.CYAN, bold=True)
    typer.secho("=" * 60, fg=typer.colors.CYAN)
    
    errors = []
    warnings = []
    
    # 1. Vérifier quests_db.json
    typer.secho("\n📁 Vérification de quests_db.json...", fg=typer.colors.CYAN)
    try:
        storage = QuestStorage()
        quests = storage.load_all_quests()
        typer.secho(f"   ✅ Fichier valide: {len(quests)} quête(s)", fg=typer.colors.GREEN)
        
        # Vérifier les IDs
        ids = [q["id"] for q in quests]
        if len(ids) != len(set(ids)):
            duplicates = [id for id in set(ids) if ids.count(id) > 1]
            typer.secho(f"   ⚠️  IDs en double: {duplicates}", fg=typer.colors.YELLOW)
            warnings.append("Utilisez 'fix-ids' pour corriger les doublons")
        
        # Vérifier la structure
        for quest in quests:
            required_fields = ["id", "title", "description", "base_xp", "type"]
            missing = [f for f in required_fields if f not in quest]
            if missing:
                typer.secho(f"   ⚠️  Quête #{quest.get('id', '?')}: champs manquants: {missing}", fg=typer.colors.YELLOW)
                warnings.append(f"Quête #{quest.get('id', '?')} incomplète")
        
    except FileNotFoundError:
        typer.secho("   ❌ Fichier introuvable", fg=typer.colors.RED)
        errors.append("quests_db.json manquant")
    except json.JSONDecodeError:
        typer.secho("   ❌ Fichier JSON corrompu", fg=typer.colors.RED)
        errors.append("quests_db.json corrompu - impossible à lire")
    except Exception as e:
        typer.secho(f"   ❌ Erreur: {str(e)}", fg=typer.colors.RED)
        errors.append(f"quests_db.json: {str(e)}")
    
    # 2. Vérifier save.json
    typer.secho("\n💾 Vérification de save.json...", fg=typer.colors.CYAN)
    try:
        player_storage = PlayerStorage()
        player = player_storage.load()
        typer.secho(f"   ✅ Sauvegarde valide: {player.name} (niveau {player.level})", fg=typer.colors.GREEN)
        typer.secho(f"      XP: {player.xp}, Argent: {player.money}, Inventaire: {len(player.inventory)} objet(s)", fg=typer.colors.WHITE)
        typer.secho(f"      Quêtes complétées: {len(player.completed_quests)}", fg=typer.colors.WHITE)
        
    except FileNotFoundError:
        typer.secho("   ⚠️  Aucune sauvegarde (sera créée au premier lancement)", fg=typer.colors.YELLOW)
    except json.JSONDecodeError:
        typer.secho("   ❌ Fichier de sauvegarde corrompu", fg=typer.colors.RED)
        errors.append("save.json corrompu")
        warnings.append("Utilisez 'reset-save' dans quest_manager pour réinitialiser")
    except Exception as e:
        typer.secho(f"   ❌ Erreur: {str(e)}", fg=typer.colors.RED)
        errors.append(f"save.json: {str(e)}")
    
    # 3. Résumé
    typer.secho("\n" + "=" * 60, fg=typer.colors.CYAN)
    typer.secho("\n📊 RÉSUMÉ", fg=typer.colors.CYAN, bold=True)
    
    if not errors and not warnings:
        typer.secho("   ✅ Tous les systèmes sont opérationnels", fg=typer.colors.GREEN, bold=True)
    else:
        if errors:
            typer.secho(f"\n   ❌ {len(errors)} erreur(s) critique(s):", fg=typer.colors.RED, bold=True)
            for error in errors:
                typer.secho(f"      • {error}", fg=typer.colors.RED)
        
        if warnings:
            typer.secho(f"\n   ⚠️  {len(warnings)} avertissement(s):", fg=typer.colors.YELLOW, bold=True)
            for warning in warnings:
                typer.secho(f"      • {warning}", fg=typer.colors.YELLOW)
    
    typer.secho("\n" + "=" * 60 + "\n", fg=typer.colors.CYAN)

def configure_decorators(current_decorators: list) -> list:
    """Interface interactive pour configurer les décorateurs"""
    decorators = current_decorators.copy()
    
    while True:
        typer.clear()
        typer.secho("\n⚙️  CONFIGURATION DES DÉCORATEURS\n", fg=typer.colors.CYAN, bold=True)
        
        if decorators:
            typer.secho("Décorateurs actuels:", fg=typer.colors.YELLOW)
            for i, dec in enumerate(decorators, 1):
                typer.secho(f"  [{i}] {dec['type']}: {dec['value']}", fg=typer.colors.WHITE)
            typer.secho()
        else:
            typer.secho("Aucun décorateur configuré\n", fg=typer.colors.YELLOW)
        
        typer.secho("[A] Ajouter un décorateur", fg=typer.colors.GREEN)
        if decorators:
            typer.secho("[D] Supprimer un décorateur", fg=typer.colors.RED)
        typer.secho("[R] Retour", fg=typer.colors.CYAN)
        
        choice = typer.prompt("\nVotre choix").strip().upper()
        
        if choice == "A":
            new_dec = add_decorator_menu()
            if new_dec:
                decorators.append(new_dec)
                typer.secho("✅ Décorateur ajouté", fg=typer.colors.GREEN)
                typer.pause()
        
        elif choice == "D" and decorators:
            try:
                index = typer.prompt("Numéro du décorateur à supprimer", type=int)
                if 1 <= index <= len(decorators):
                    removed = decorators.pop(index - 1)
                    typer.secho(f"✅ Décorateur supprimé: {removed['type']}", fg=typer.colors.GREEN)
                else:
                    typer.secho("❌ Numéro invalide", fg=typer.colors.RED)
            except ValueError:
                typer.secho("❌ Veuillez entrer un nombre", fg=typer.colors.RED)
            typer.pause()
        
        elif choice == "R":
            break
        else:
            typer.secho("❌ Choix invalide", fg=typer.colors.RED)
            typer.pause()
    
    return decorators


def add_decorator_menu() -> Optional[Dict]:
    """Menu pour ajouter un décorateur"""
    typer.secho("\nTypes de décorateurs:", fg=typer.colors.CYAN)
    typer.secho("  [1] Condition : Niveau requis", fg=typer.colors.WHITE)
    typer.secho("  [2] Condition : PNJ requis", fg=typer.colors.WHITE)
    typer.secho("  [3] Récompense : Argent", fg=typer.colors.WHITE)
    typer.secho("  [4] Récompense : Objet", fg=typer.colors.WHITE)
    typer.secho("  [Q] Annuler", fg=typer.colors.YELLOW)
    
    choice = typer.prompt("\nVotre choix").strip()
    
    if choice == "1":
        try:
            level = typer.prompt("Niveau minimum", type=int)
            if level <= 0:
                typer.secho("❌ Le niveau doit être positif", fg=typer.colors.RED)
                typer.pause()
                return None
            return {"type": "level_req", "value": level}
        except ValueError:
            typer.secho("❌ Valeur invalide", fg=typer.colors.RED)
            typer.pause()
            return None
    
    elif choice == "2":
        npc_name = typer.prompt("Nom du PNJ")
        if not npc_name.strip():
            typer.secho("❌ Le nom ne peut pas être vide", fg=typer.colors.RED)
            typer.pause()
            return None
        return {"type": "npc_req", "value": npc_name}
    
    elif choice == "3":
        try:
            amount = typer.prompt("Montant en pièces", type=int)
            if amount <= 0:
                typer.secho("❌ Le montant doit être positif", fg=typer.colors.RED)
                typer.pause()
                return None
            return {"type": "money_reward", "value": amount}
        except ValueError:
            typer.secho("❌ Valeur invalide", fg=typer.colors.RED)
            typer.pause()
            return None
    
    elif choice == "4":
        item_name = typer.prompt("Nom de l'objet")
        if not item_name.strip():
            typer.secho("❌ Le nom ne peut pas être vide", fg=typer.colors.RED)
            typer.pause()
            return None
        return {"type": "item_reward", "value": item_name}
    
    elif choice.upper() == "Q":
        return None
    
    else:
        typer.secho("❌ Choix invalide", fg=typer.colors.RED)
        typer.pause()
        return None


if __name__ == "__main__":
    app()