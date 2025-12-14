#!/usr/bin/env python3
"""
Script de nettoyage des IDs orphelins dans users.json
À exécuter depuis backend/
"""

import json
import sys
from pathlib import Path

def clean_orphan_ids():
    """Nettoie les IDs de quêtes qui n'existent plus"""
    
    # Chemins
    users_file = Path("data/users.json")
    quests_file = Path("data/quests_db.json")
    
    if not users_file.exists() or not quests_file.exists():
        print("❌ Fichiers data/users.json ou data/quests_db.json introuvables")
        print("   Assurez-vous d'être dans le dossier backend/")
        sys.exit(1)
    
    # Charger les données
    with open(users_file, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    with open(quests_file, 'r', encoding='utf-8') as f:
        quests = json.load(f)
    
    # IDs valides
    valid_ids = {q["id"] for q in quests}
    print(f"✅ IDs de quêtes valides : {sorted(valid_ids)}")
    
    # Nettoyer chaque utilisateur
    total_cleaned = 0
    for username, user_data in users.items():
        old_completed = user_data.get("completed_quests", [])
        new_completed = [qid for qid in old_completed if qid in valid_ids]
        
        if len(new_completed) != len(old_completed):
            removed = set(old_completed) - set(new_completed)
            print(f"\n🧹 Utilisateur '{username}':")
            print(f"   Avant  : {old_completed}")
            print(f"   Après  : {new_completed}")
            print(f"   Retiré : {sorted(removed)}")
            
            user_data["completed_quests"] = new_completed
            total_cleaned += len(removed)
    
    if total_cleaned == 0:
        print("\n✅ Aucun ID orphelin trouvé ! Tout est propre.")
        return
    
    # Sauvegarder
    backup_file = users_file.with_suffix('.json.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Backup créé : {backup_file}")
    
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Nettoyage terminé ! {total_cleaned} ID(s) orphelin(s) retiré(s)")
    print(f"   Fichier mis à jour : {users_file}")

if __name__ == "__main__":
    print("🧹 Nettoyage des IDs de quêtes orphelins")
    print("=" * 50)
    clean_orphan_ids()