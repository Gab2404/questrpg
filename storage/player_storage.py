import json
import os
from dataclasses import asdict
from models.player import Player

SAVE_FILE = "data/save.json"

def load_player() -> Player:
    """Charge le joueur depuis le fichier de sauvegarde"""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return Player(**data)
            except:
                pass
    return Player(name="Héros")

def save_player(player: Player):
    """Sauvegarde le joueur dans le fichier JSON"""
    os.makedirs("data", exist_ok=True)
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(player), f, indent=4, ensure_ascii=False)