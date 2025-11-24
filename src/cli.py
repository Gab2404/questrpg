import typer
from typing import Dict, List

from player import Player
from quest_factory import QuestFactory
from quest_types import CollectQuest, ExplorationQuest, CombatQuest
from events import EventManager, ConsoleObserver

app = typer.Typer()

# --- stockage en mémoire pour la démo ---
players: Dict[str, Player] = {}
quests: List[object] = []

# --- système d'événements (Observer) ---
event_manager = EventManager()
console_observer = ConsoleObserver()
event_manager.subscribe("quest_completed", console_observer)


def attach_event_manager(quest) -> None:
    """Attache l'EventManager à une quête et à ses sous-quêtes éventuelles."""
    if hasattr(quest, "set_event_manager"):
        quest.set_event_manager(event_manager)
    if hasattr(quest, "get_subquests"):
        for sub in quest.get_subquests():
            attach_event_manager(sub)


@app.command()
def create_player(name: str):
    """Créer un joueur."""
    if name in players:
        typer.echo("Ce joueur existe déjà.")
        raise typer.Exit(code=1)
    players[name] = Player(name)
    typer.echo("Joueur créé : {0}".format(name))


@app.command()
def list_players():
    """Lister les joueurs."""
    if not players:
        typer.echo("Aucun joueur.")
        return
    for player in players.values():
        typer.echo("- {0} (XP={1})".format(player.name, player.xp))


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
    attach_event_manager(quest)
    quests.append(quest)
    typer.echo(
        "Quête de collecte créée : {0} (collecter {1} {2})".format(
            name, amount, item_name
        )
    )


@app.command()
def create_demo_main_quest():
    """Créer une quête principale de démo avec deux sous-quêtes."""
    sub1 = QuestFactory.create_collect_quest(
        name="Collecte d'herbes",
        description="Ramasser 5 herbes médicinales",
        item_name="Herbe",
        amount=5,
    )
    sub2 = QuestFactory.create_combat_quest(
        name="Chasse aux loups",
        description="Vaincre 3 loups.",
        enemy_name="Loup",
        kills=3,
        difficulty=2,
    )
    main_quest = QuestFactory.create_main_quest(
        name="Sauver le village",
        description="Aider le village avec différentes tâches.",
        subquests=[sub1, sub2],
    )
    attach_event_manager(main_quest)
    quests.append(main_quest)
    typer.echo(
        "Quête principale de démo créée : 'Sauver le village' (index {0})".format(
            len(quests) - 1
        )
    )


@app.command()
def list_quests():
    """Lister toutes les quêtes existantes."""
    if not quests:
        typer.echo("Aucune quête.")
        return
    for index, quest in enumerate(quests):
        try:
            completed = quest.is_completed()
        except Exception:
            completed = False
        status = "complétée" if completed else "non complétée"
        typer.echo("{0}: {1} [{2}]".format(index, quest.name, status))


@app.command()
def accept_quest(player_name: str, quest_index: int):
    """Un joueur accepte une quête par son index."""
    player = players.get(player_name)
    if player is None:
        typer.echo("Joueur introuvable.")
        raise typer.Exit(code=1)

    try:
        quest = quests[quest_index]
    except IndexError:
        typer.echo("Index de quête invalide.")
        raise typer.Exit(code=1)

    player.accept_quest(quest)
    typer.echo("{0} a accepté la quête '{1}'.".format(player.name, quest.name))


@app.command()
def progress_collect(player_name: str, quest_index: int, amount: int = 1):
    """Ajouter de la progression sur une quête de collecte."""
    player = players.get(player_name)
    if player is None:
        typer.echo("Joueur introuvable.")
        raise typer.Exit(code=1)

    try:
        quest = quests[quest_index]
    except IndexError:
        typer.echo("Index de quête invalide.")
        raise typer.Exit(code=1)

    if not isinstance(quest, CollectQuest):
        typer.echo("Cette quête n'est pas une quête de collecte.")
        raise typer.Exit(code=1)

    quest.add_item(amount)
    typer.echo(
        "Progression mise à jour : {0}/{1} {2}".format(
            quest.current_amount, quest.required_amount, quest.item_name
        )
    )


@app.command()
def progress_combat(player_name: str, quest_index: int, kills: int = 1):
    """Ajouter des kills sur une quête de combat."""
    player = players.get(player_name)
    if player is None:
        typer.echo("Joueur introuvable.")
        raise typer.Exit(code=1)

    try:
        quest = quests[quest_index]
    except IndexError:
        typer.echo("Index de quête invalide.")
        raise typer.Exit(code=1)

    if not isinstance(quest, CombatQuest):
        typer.echo("Cette quête n'est pas une quête de combat.")
        raise typer.Exit(code=1)

    quest.add_kill(kills)
    typer.echo(
        "Kills mis à jour : {0}/{1} {2}".format(
            quest.current_kills, quest.required_kills, quest.enemy_name
        )
    )


@app.command()
def mark_explored(player_name: str, quest_index: int):
    """Marquer une quête d'exploration comme visitée."""
    player = players.get(player_name)
    if player is None:
        typer.echo("Joueur introuvable.")
        raise typer.Exit(code=1)

    try:
        quest = quests[quest_index]
    except IndexError:
        typer.echo("Index de quête invalide.")
        raise typer.Exit(code=1)

    if not isinstance(quest, ExplorationQuest):
        typer.echo("Cette quête n'est pas une quête d'exploration.")
        raise typer.Exit(code=1)

    quest.mark_visited()
    typer.echo("Lieu visité pour la quête '{0}'.".format(quest.name))


@app.command()
def complete_quest(player_name: str, quest_index: int):
    """Tente de compléter une quête pour un joueur."""
    player = players.get(player_name)
    if player is None:
        typer.echo("Joueur introuvable.")
        raise typer.Exit(code=1)

    try:
        quest = quests[quest_index]
    except IndexError:
        typer.echo("Index de quête invalide.")
        raise typer.Exit(code=1)

    before_xp = player.xp
    player.complete_quest(quest)

    if player.xp == before_xp:
        typer.echo("La quête n'est pas encore complétée ou déjà résolue.")
    else:
        typer.echo(
            "Quête complétée ! Nouveau total d'XP pour {0}: {1}".format(
                player.name, player.xp
            )
        )


if __name__ == "__main__":
    app()
