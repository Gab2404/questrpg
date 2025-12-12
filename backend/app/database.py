import json
import os
from typing import List, Dict, Optional
from app.config import settings

class Database:
    """Gestionnaire de base de données JSON"""
    
    def __init__(self):
        self._ensure_data_directory()
        self._ensure_files()
    
    def _ensure_data_directory(self):
        if not os.path.exists(settings.DATA_DIR):
            os.makedirs(settings.DATA_DIR)
    
    def _ensure_files(self):
        if not os.path.exists(settings.USERS_DB_FILE):
            self._save_json(settings.USERS_DB_FILE, {})
        
        if not os.path.exists(settings.QUESTS_DB_FILE):
            self._save_json(settings.QUESTS_DB_FILE, [])
    
    def _load_json(self, filepath: str) -> any:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _save_json(self, filepath: str, data: any):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Users
    def get_all_users(self) -> Dict:
        return self._load_json(settings.USERS_DB_FILE) or {}
    
    def get_user(self, username: str) -> Optional[Dict]:
        users = self.get_all_users()
        return users.get(username)
    
    def save_user(self, username: str, user_data: Dict):
        users = self.get_all_users()
        users[username] = user_data
        self._save_json(settings.USERS_DB_FILE, users)
    
    def update_user(self, username: str, user_data: Dict):
        self.save_user(username, user_data)
    
    def user_exists(self, username: str) -> bool:
        users = self.get_all_users()
        return username in users
    
    # Quests
    def get_all_quests(self) -> List[Dict]:
        return self._load_json(settings.QUESTS_DB_FILE) or []
    
    def get_quest(self, quest_id: int) -> Optional[Dict]:
        quests = self.get_all_quests()
        for quest in quests:
            if quest.get("id") == quest_id:
                return quest
        return None
    
    def save_quests(self, quests: List[Dict]):
        self._save_json(settings.QUESTS_DB_FILE, quests)
    
    def add_quest(self, quest_data: Dict) -> Dict:
        quests = self.get_all_quests()
        quests.append(quest_data)
        self.save_quests(quests)
        return quest_data
    
    def update_quest(self, quest_id: int, quest_data: Dict) -> Optional[Dict]:
        quests = self.get_all_quests()
        for i, quest in enumerate(quests):
            if quest.get("id") == quest_id:
                quests[i] = quest_data
                self.save_quests(quests)
                return quest_data
        return None
    
    def delete_quest(self, quest_id: int) -> bool:
        quests = self.get_all_quests()
        filtered = [q for q in quests if q.get("id") != quest_id]
        if len(filtered) < len(quests):
            self.save_quests(filtered)
            return True
        return False
    
    def get_next_quest_id(self) -> int:
        quests = self.get_all_quests()
        if not quests:
            return 1
        return max(q.get("id", 0) for q in quests) + 1

db = Database()