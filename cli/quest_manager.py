import typer
import os
from models.player import Player
from quests.quest_factory import QuestFactory
from storage.player_storage import load_player, save_player

app = typer.Typer()
state = {"player": None, "quests": []}

@app.callback()
def main():
    """Initialise l'application (charge joueur et quêtes)"""
    state["player"] = load_player()
    state["quests"] = QuestFactory.load_from_json()

@app.command()
def status():
    """Affiche le statut complet du joueur"""
    p = state["player"]
    typer.echo("╔═══════════════════════════════╗")
    typer.echo("║      STATUT DU JOUEUR         ║")
    typer.echo("╚═══════════════════════════════╝")
    typer.echo(f"👤 Nom       : {p.name}")
    typer.echo(f"⭐ Niveau    : {p.level}")
    typer.echo(f"✨ XP        : {p.xp}/{100 * p.level}")
    typer.echo(f"💰 Or        : {p.money}")
    typer.echo(f"💬 PNJ Parlé : {'Oui' if p.spoken_to_npc else 'Non'}")
    typer.echo(f"✅ Quêtes complétées : {len(p.completed_quests)}")
    typer.echo(f"🎒 Inventaire : {', '.join(p.inventory) if p.inventory else 'Vide'}")

@app.command()
def list_quests():
    """Liste toutes les quêtes avec leur statut"""
    if not state["quests"]:
        typer.secho("🔭 Aucune quête disponible.", fg=typer.colors.YELLOW)
        return
    
    typer.echo("\n╔════════════════════════════════════════════════════════╗")
    typer.echo("║               TABLEAU DES QUÊTES                       ║")
    typer.echo("╚════════════════════════════════════════════════════════╝\n")
    
    player = state["player"]
    
    for idx, q in enumerate(state["quests"], start=1):
        if q.is_completed(player):
            status_icon = typer.style("✅ TERMINÉE", fg=typer.colors.GREEN, bold=True)
        else:
            status_icon = typer.style("🆕 DISPONIBLE", fg=typer.colors.CYAN)
        
        typer.echo(f"{idx}. {status_icon}")
        typer.echo(f"   {q.get_description()}")
        typer.echo("")

@app.command()
def talk_npc():
    """Simule une conversation avec un PNJ"""
    state["player"].spoken_to_npc = True
    typer.secho("🗣️  Vous avez discuté avec le PNJ.", fg=typer.colors.GREEN)
    save_player(state["player"])

@app.command()
def do_quest(quest_number: int):
    """
    Tente d'accomplir une quête
    
    Args:
        quest_number: Numéro de la quête (correspond à l'ordre d'affichage)
    """
    quests = state["quests"]
    
    if quest_number < 1 or quest_number > len(quests):
        typer.secho("❌ Numéro de quête invalide.", fg=typer.colors.RED)
        return

    quest = quests[quest_number - 1]
    player = state["player"]

    typer.echo(f"\n⚔️  Tentative de quête : {quest.get_description()}")
    typer.echo("-" * 60)
    
    if quest.can_start(player):
        typer.secho("🎉 SUCCÈS ! Quête validée.", fg=typer.colors.GREEN, bold=True)
        quest.complete(player)
        save_player(player)
    else:
        typer.secho("❌ Impossible de faire la quête.", fg=typer.colors.RED)

@app.command()
def cheat_level(level: int):
    """
    Change le niveau du joueur (pour tester)
    
    Args:
        level: Nouveau niveau
    """
    if level < 1:
        typer.secho("❌ Le niveau doit être >= 1", fg=typer.colors.RED)
        return
    
    state["player"].level = level
    state["player"].xp = 0
    save_player(state["player"])
    typer.secho(f"🎮 Niveau modifié : {level}", fg=typer.colors.YELLOW)

@app.command()
def reset_save():
    """Supprime la sauvegarde pour recommencer à zéro"""
    save_file = "data/save.json"
    if os.path.exists(save_file):
        os.remove(save_file)
        typer.secho("♻️  Sauvegarde supprimée.", fg=typer.colors.YELLOW)
        state["player"] = Player(name="Héros")
    else:
        typer.secho("ℹ️  Aucune sauvegarde à supprimer.", fg=typer.colors.BLUE)

if __name__ == "__main__":
    app()