import json
import os
from typing import List, Dict, Any

DB_FILE = "data/quests_db.json"

def load_quests_db() -> List[Dict[str, Any]]:
    """Charge la base de données des quêtes (format JSON brut)"""
    if not os.path.exists(DB_FILE):
        return []
    
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except json.JSONDecodeError:
        return []

def save_quests_db(data: List[Dict[str, Any]]):
    """Sauvegarde la base de données des quêtes"""
    os.makedirs("data", exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)