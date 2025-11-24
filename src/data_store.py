# src/data_store.py
import json
from typing import Dict
from pathlib import Path

from player import Player

DATA_FILE = Path(__file__).parent / "data_players.json"


def save_players(players: Dict[str, Player]) -> None:
    """Sauvegarde minimale des joueurs (name, level, xp) dans un JSON."""
    data = {}
    for name, player in players.items():
        data[name] = {
            "name": player.name,
            "level": player.level,
            "xp": player.xp,
        }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_players() -> Dict[str, Player]:
    """Charge les joueurs depuis le JSON. Si fichier absent, renvoie {}."""
    if not DATA_FILE.exists():
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

    players: Dict[str, Player] = {}
    for name, pdata in raw.items():
        p = Player(pdata.get("name", name))
        p.level = int(pdata.get("level", 1))
        p.xp = int(pdata.get("xp", 0))
        players[name] = p
    return players
