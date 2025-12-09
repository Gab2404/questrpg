import typer
import json
from functools import wraps
from storage.quest_storage import QuestStorage
from storage.player_storage import PlayerStorage
from quests.quest_factory import QuestFactory

app = typer.Typer(help="Interface de gestion des quêtes pour le joueur")

# ============================================================================
# GESTION D'ERREURS GLOBALE
# ============================================================================

def safe_command(func):
    """Décorateur pour gérer les erreurs de manière élégante"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except typer.Exit:
            raise
        except FileNotFoundError as e:
            typer.secho(f"❌ Fichier introuvable: {e}", fg=typer.colors.RED)
            typer.secho("💡 Le jeu va créer les fichiers nécessaires", fg=typer.colors.YELLOW)
            raise typer.Exit(1)
        except json.JSONDecodeError:
            typer.secho("❌ Fichier de sauvegarde corrompu", fg=typer.colors.RED)
            typer.secho("💡 Utilisez 'reset-save' pour réinitialiser", fg=typer.colors.YELLOW)
            raise typer.Exit(1)
        except Exception as e:
            typer.secho(f"❌ Erreur inattendue: {str(e)}", fg=typer.colors.RED)
            typer.secho("💡 Utilisez --help pour l'aide", fg=typer.colors.YELLOW)
            raise typer.Exit(1)
    return wrapper


# ============================================================================
# COMMANDES
# ============================================================================

@app.command()
@safe_command
def status():
    """Affiche le statut actuel du joueur"""
    player_storage = PlayerStorage()
    player = player_storage.load()
    quest_storage = QuestStorage()
    
    typer.secho("\n╔════════════════════════════════════════╗", fg=typer.colors.CYAN)
    typer.secho("║         STATUT DU JOUEUR               ║", fg=typer.colors.CYAN)
    typer.secho("╠════════════════════════════════════════╣", fg=typer.colors.CYAN)
    typer.secho(f"║ Nom      : {player.name.ljust(28)} ║", fg=typer.colors.WHITE)
    typer.secho(f"║ Niveau   : {str(player.level).ljust(28)} ║", fg=typer.colors.WHITE)
    typer.secho(f"║ XP       : {str(player.xp).ljust(28)} ║", fg=typer.colors.WHITE)
    typer.secho(f"║ Argent   : {str(player.money).ljust(20)} pièces d'or ║", fg=typer.colors.WHITE)
    typer.secho("╠════════════════════════════════════════╣", fg=typer.colors.CYAN)
    
    if player.inventory:
        typer.secho("║ 🎒 INVENTAIRE                          ║", fg=typer.colors.YELLOW)
        for item in player.inventory:
            item_str = f"   • {item}"[:36]
            typer.secho(f"║ {item_str.ljust(38)} ║", fg=typer.colors.WHITE)
    else:
        typer.secho("║ 🎒 INVENTAIRE : Vide                   ║", fg=typer.colors.YELLOW)
    
    typer.secho("╠════════════════════════════════════════╣", fg=typer.colors.CYAN)
    
    if player.completed_quests:
        typer.secho("║ ✅ QUÊTES COMPLÉTÉES                   ║", fg=typer.colors.GREEN)
        for quest_id in player.completed_quests:
            try:
                quest = quest_storage.get_quest_by_id(quest_id)
                quest_str = f"   #{quest_id} - {quest['title']}"[:36]
                typer.secho(f"║ {quest_str.ljust(38)} ║", fg=typer.colors.WHITE)
            except:
                typer.secho(f"║   #{quest_id} - [Quête supprimée]               ║", fg=typer.colors.RED)
    else:
        typer.secho("║ ✅ QUÊTES COMPLÉTÉES : Aucune          ║", fg=typer.colors.YELLOW)
    
    typer.secho("╚════════════════════════════════════════╝\n", fg=typer.colors.CYAN)


@app.command()
@safe_command
def list_quests():
    """Liste toutes les quêtes disponibles"""
    quest_storage = QuestStorage()
    player_storage = PlayerStorage()
    
    quests = quest_storage.load_all_quests()
    player = player_storage.load()
    
    if not quests:
        typer.secho("\nℹ️  Aucune quête disponible pour le moment", fg=typer.colors.YELLOW)
        typer.secho("💡 Contactez l'administrateur pour créer des quêtes\n", fg=typer.colors.CYAN)
        return
    
    typer.secho("\n╔════════════════════════════════════════════════════════════╗", fg=typer.colors.CYAN)
    typer.secho("║                    QUÊTES DISPONIBLES                      ║", fg=typer.colors.CYAN)
    typer.secho("╠════════════════════════════════════════════════════════════╣", fg=typer.colors.CYAN)
    
    for quest_data in quests:
        quest_id = quest_data["id"]
        is_completed = quest_id in player.completed_quests
        
        # Statut
        status_icon = "✅" if is_completed else "🆕"
        status_color = typer.colors.GREEN if is_completed else typer.colors.CYAN
        
        typer.secho(f"║ {status_icon} #{quest_id} - {quest_data['title'][:50].ljust(50)} ║", fg=status_color)
        
        # Type et XP
        quest_type = "Principale" if quest_data["type"] == "PRIMARY" else "Secondaire"
        xp_info = f"Type: {quest_type} | XP: {quest_data['base_xp']}"
        
        # Calculer les bonus
        decorators = quest_data.get("decorators", [])
        has_rewards = any(d["type"] in ["money_reward", "item_reward"] for d in decorators)
        if has_rewards:
            xp_info += " + bonus"
        
        typer.secho(f"║    {xp_info.ljust(56)} ║", fg=typer.colors.WHITE)
        
        if not is_completed:
            # Conditions
            conditions = []
            rewards = []
            
            for dec in decorators:
                if dec["type"] == "level_req":
                    met = player.level >= dec["value"]
                    symbol = "✓" if met else "✗"
                    color = typer.colors.GREEN if met else typer.colors.RED
                    conditions.append((f"Niveau requis: {dec['value']}", color, symbol))
                
                elif dec["type"] == "npc_req":
                    met = player.spoken_to_npc
                    symbol = "✓" if met else "✗"
                    color = typer.colors.GREEN if met else typer.colors.RED
                    conditions.append((f"Parler au PNJ requis", color, symbol))
                
                elif dec["type"] == "money_reward":
                    rewards.append(f"+{dec['value']} pièces")
                
                elif dec["type"] == "item_reward":
                    rewards.append(dec['value'])
            
            if conditions:
                cond_strs = [f"{s} {cond}" for cond, _, s in conditions]
                cond_line = ", ".join(cond_strs)
                typer.secho(f"║    {cond_line[:56].ljust(56)} ║", fg=typer.colors.YELLOW)
            
            if rewards:
                reward_line = f"Récompenses: {', '.join(rewards)}"
                typer.secho(f"║    {reward_line[:56].ljust(56)} ║", fg=typer.colors.MAGENTA)
        
        typer.secho("║                                                            ║", fg=typer.colors.CYAN)
    
    typer.secho("╚════════════════════════════════════════════════════════════╝\n", fg=typer.colors.CYAN)
    
    # Statistiques
    completed_count = len(player.completed_quests)
    total_count = len(quests)
    typer.secho(f"📊 Progression: {completed_count}/{total_count} quêtes complétées\n", fg=typer.colors.YELLOW)


@app.command()
@safe_command
def talk_npc():
    """Simule une conversation avec un PNJ"""
    player_storage = PlayerStorage()
    player = player_storage.load()
    
    if player.spoken_to_npc:
        typer.secho("\n💬 Vous avez déjà parlé au PNJ principal.", fg=typer.colors.YELLOW)
        typer.secho("   Il n'a rien de nouveau à vous dire pour le moment.\n", fg=typer.colors.WHITE)
        return
    
    typer.secho("\n" + "="*60, fg=typer.colors.CYAN)
    typer.secho("💬 CONVERSATION AVEC LE PNJ", fg=typer.colors.CYAN, bold=True)
    typer.secho("="*60, fg=typer.colors.CYAN)
    
    typer.secho("\n🧙 PNJ: Bienvenue, aventurier !", fg=typer.colors.GREEN)
    typer.secho("       Je vois que vous êtes nouveau ici.", fg=typer.colors.WHITE)
    typer.secho("       Certaines quêtes nécessitent mon aide...\n", fg=typer.colors.WHITE)
    
    typer.pause("Appuyez sur Entrée pour continuer...")
    
    player.spoken_to_npc = True
    player_storage.save(player)
    
    typer.secho("\n✅ Vous avez maintenant accès aux quêtes nécessitant un PNJ !", fg=typer.colors.GREEN, bold=True)
    typer.secho("   Utilisez 'list-quests' pour voir les nouvelles quêtes débloquées.\n", fg=typer.colors.CYAN)


@app.command()
@safe_command
def do_quest(quest_id: int):
    """Tente d'accomplir une quête"""
    # Validation de l'ID
    if quest_id <= 0:
        typer.secho("❌ L'ID doit être un nombre positif", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    quest_storage = QuestStorage()
    player_storage = PlayerStorage()
    
    # Vérifier que la quête existe
    if not quest_storage.quest_exists(quest_id):
        typer.secho(f"❌ Aucune quête avec l'ID {quest_id}", fg=typer.colors.RED)
        typer.secho("💡 Utilisez 'list-quests' pour voir les quêtes disponibles", fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    
    # Charger le joueur
    player = player_storage.load()
    
    # Vérifier si déjà complétée
    if quest_id in player.completed_quests:
        typer.secho(f"\n⚠️  Vous avez déjà complété cette quête !", fg=typer.colors.YELLOW)
        typer.secho("   Les quêtes ne peuvent être accomplies qu'une seule fois.\n", fg=typer.colors.WHITE)
        raise typer.Exit(0)
    
    # Construire la quête avec ses décorateurs
    quest_data = quest_storage.get_quest_by_id(quest_id)
    quest = QuestFactory.create_quest_from_dict(quest_data)
    
    typer.secho(f"\n🎯 Tentative d'accomplissement de la quête #{quest_id}...", fg=typer.colors.CYAN)
    typer.secho(f"   {quest_data['title']}\n", fg=typer.colors.WHITE)
    
    # Tenter de compléter
    result = quest.complete(player)
    
    if result:
        typer.secho("✅ Conditions remplies !", fg=typer.colors.GREEN)
        typer.secho("━" * 60, fg=typer.colors.GREEN)
        typer.secho(f"🎊 QUÊTE TERMINÉE : {quest_data['title']}\n", fg=typer.colors.BRIGHT_GREEN, bold=True)
        
        # Afficher les récompenses
        typer.secho("Récompenses obtenues :", fg=typer.colors.CYAN)
        typer.secho(f"  ⭐ +{quest.get_xp_reward()} XP", fg=typer.colors.YELLOW)
        
        # Détecter les récompenses supplémentaires
        for dec in quest_data.get("decorators", []):
            if dec["type"] == "money_reward":
                typer.secho(f"  💰 +{dec['value']} pièces d'or", fg=typer.colors.YELLOW)
            elif dec["type"] == "item_reward":
                typer.secho(f"  🎁 {dec['value']} ajouté à l'inventaire", fg=typer.colors.YELLOW)
        
        typer.secho("━" * 60 + "\n", fg=typer.colors.GREEN)
        
        # Marquer comme complétée
        player.completed_quests.append(quest_id)
        player_storage.save(player)
        
        typer.secho("💡 Utilisez 'status' pour voir votre progression\n", fg=typer.colors.CYAN)
    else:
        typer.secho("❌ Vous ne remplissez pas les conditions requises\n", fg=typer.colors.RED)
        
        # Afficher les conditions manquantes
        typer.secho("Conditions à remplir :", fg=typer.colors.YELLOW)
        for dec in quest_data.get("decorators", []):
            if dec["type"] == "level_req":
                if player.level < dec["value"]:
                    typer.secho(f"  ✗ Niveau requis: {dec['value']} (actuel: {player.level})", fg=typer.colors.RED)
                else:
                    typer.secho(f"  ✓ Niveau requis: {dec['value']}", fg=typer.colors.GREEN)
            
            elif dec["type"] == "npc_req":
                if not player.spoken_to_npc:
                    typer.secho(f"  ✗ Vous devez parler au PNJ (utilisez 'talk-npc')", fg=typer.colors.RED)
                else:
                    typer.secho(f"  ✓ PNJ contacté", fg=typer.colors.GREEN)
        
        typer.secho()
        raise typer.Exit(1)


@app.command()
@safe_command
def cheat_level(level: int):
    """Modifie le niveau du joueur (triche)"""
    if level <= 0:
        typer.secho("❌ Le niveau doit être un nombre positif", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    if level > 100:
        typer.secho("⚠️  Niveau très élevé ! Maximum recommandé: 100", fg=typer.colors.YELLOW)
        confirm = typer.confirm(f"Êtes-vous sûr de vouloir passer niveau {level} ?", default=False)
        if not confirm:
            typer.secho("❌ Opération annulée", fg=typer.colors.YELLOW)
            raise typer.Exit(0)
    
    player_storage = PlayerStorage()
    player = player_storage.load()
    
    old_level = player.level
    player.level = level
    player_storage.save(player)
    
    typer.secho(f"\n🎮 TRICHE ACTIVÉE", fg=typer.colors.MAGENTA, bold=True)
    typer.secho(f"   Niveau: {old_level} → {level}", fg=typer.colors.YELLOW)
    typer.secho(f"   Vous pouvez maintenant tenter des quêtes de niveau {level}\n", fg=typer.colors.CYAN)


@app.command()
@safe_command
def reset_save():
    """Réinitialise la sauvegarde du joueur"""
    import os
    
    save_path = "data/save.json"
    
    if not os.path.exists(save_path):
        typer.secho("\nℹ️  Aucune sauvegarde à supprimer", fg=typer.colors.YELLOW)
        return
    
    typer.secho("\n⚠️  RÉINITIALISATION DE LA SAUVEGARDE", fg=typer.colors.RED, bold=True)
    typer.secho("   Toute votre progression sera perdue :", fg=typer.colors.YELLOW)
    
    try:
        player_storage = PlayerStorage()
        player = player_storage.load()
        
        typer.secho(f"   • Niveau {player.level}", fg=typer.colors.WHITE)
        typer.secho(f"   • {player.xp} XP", fg=typer.colors.WHITE)
        typer.secho(f"   • {player.money} pièces d'or", fg=typer.colors.WHITE)
        typer.secho(f"   • {len(player.inventory)} objet(s)", fg=typer.colors.WHITE)
        typer.secho(f"   • {len(player.completed_quests)} quête(s) complétée(s)", fg=typer.colors.WHITE)
    except:
        typer.secho("   [Impossible de lire la sauvegarde actuelle]", fg=typer.colors.RED)
    
    confirm = typer.confirm("\n⚠️  Êtes-vous absolument sûr ?", default=False)
    
    if not confirm:
        typer.secho("❌ Réinitialisation annulée", fg=typer.colors.YELLOW)
        raise typer.Exit(0)
    
    # Supprimer le fichier
    os.remove(save_path)
    
    typer.secho("\n✅ Sauvegarde réinitialisée avec succès", fg=typer.colors.GREEN)
    typer.secho("   Une nouvelle sauvegarde sera créée au prochain lancement\n", fg=typer.colors.CYAN)


if __name__ == "__main__":
    app()