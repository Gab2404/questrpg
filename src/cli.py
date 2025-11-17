# src/cli.py
import typer
from player import Player
from quest_factory import QuestFactory

app = typer.Typer()

# --- faux "storage" global pour la démo ---
players: dict[str, Player] = {}
quests = []  # tu peux structurer mieux si besoin


@app.command()
def create_player(name: str):
    """Créer un joueur."""
    if name in players:
        typer.echo(f"Le joueur {name} existe déjà.")
        raise typer.Exit(code=1)
    players[name] = Player(name)
    typer.echo(f"Joueur créé : {name}")


@app.command()
def list_players():
    """Lister les joueurs."""
    if not players:
        typer.echo("Aucun joueur.")
        return
    for p in players.values():
        typer.echo(f"- {p.name} (lvl {p.level}, XP {p.xp})")


@app.command()
def create_collect_quest(
    name: str,
    description: str,
    item_name: str,
    amount: int = typer.Argument(1),
):
    """Créer une quête de collecte."""
    quest = QuestFactory.create_collect_quest(
        name=name,
        description=description,
        item_name=item_name,
        amount=amount,
    )
    quests.append(quest)
    typer.echo(f"Quête créée : {name} (collecter {amount} {item_name})")


@app.command()
def list_quests():
    """Lister les quêtes."""
    if not quests:
        typer.echo("Aucune quête.")
        return
    for i, q in enumerate(quests):
        status = "complétée" if q.is_completed() else "en cours"
        typer.echo(f"{i}: {q.name} [{status}]")


@app.command()
def accept_quest(player_name: str, quest_index: int):
    """Un joueur accepte une quête."""
    player = players.get(player_name)
    if not player:
        typer.echo("Joueur introuvable.")
        raise typer.Exit(code=1)

    try:
        quest = quests[quest_index]
    except IndexError:
        typer.echo("Index de quête invalide.")
        raise typer.Exit(code=1)

    player.accept_quest(quest)
    typer.echo(f"{player.name} a accepté la quête '{quest.name}'.")


@app.command()
def complete_quest(player_name: str, quest_index: int):
    """Forcer la complétion d'une quête (pour la démo)."""
    player = players.get(player_name)
    if not player:
        typer.echo("Joueur introuvable.")
        raise typer.Exit(code=1)

    try:
        quest = quests[quest_index]
    except IndexError:
        typer.echo("Index de quête invalide.")
        raise typer.Exit(code=1)

    # normalement: tu ferais avancer la quête (ajouter des kills, items, etc.)
    # ici pour tester on suppose qu'elle est complétée
    if not quest.is_completed():
        typer.echo("La quête n'est pas encore marquée comme complétée côté logique.")
        # tu peux choisir de quand même donner les récompenses pour les tests

    player.complete_quest(quest)


if __name__ == "__main__":
    app()
