# 🧾 Inventaire & Quêtes – CLI Documentation

Ce projet est un système d’inventaire et de quêtes en Python utilisant la POO, le pattern Strategy, le pattern Composite et un Event Manager.

Ce README répertorie **toutes les commandes disponibles dans le CLI**, avec exemples.

---

# 📦 Installation

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

Lancement du CLI :

```bash
python src/cli.py
```

Ou avec une commande directe :

```bash
python src/cli.py <commande> [options]
```

---

# 🧙 Joueurs

### ➤ **Créer un joueur**
```bash
python src/cli.py create-player <nom> <classe>
```

**Exemple :**
```bash
python src/cli.py create-player Arkon Guerrier
```

---

### ➤ **Lister les joueurs**
```bash
python src/cli.py list-players
```

Affiche soit la liste, soit “Aucun joueur”.

---

### ➤ **Inventaire d’un joueur**
```bash
python src/cli.py show-inventory <player_id>
```

---

# 🧰 Objets

### ➤ **Créer un objet**
```bash
python src/cli.py create-item <nom> <type> <valeur>
```

Types possibles : `arme`, `armure`, `potion`, `ressource`, …

**Exemple :**
```bash
python src/cli.py create-item Excalibur arme 250
```

---

### ➤ **Lister les objets**
```bash
python src/cli.py list-items
```

---

### ➤ **Donner un objet à un joueur**
```bash
python src/cli.py give-item <player_id> <item_id>
```

**Exemple :**
```bash
python src/cli.py give-item 1 3
```

---

# 🎯 Quêtes

Les quêtes utilisent :

- **XP Strategy** (gain d’XP variable selon la difficulté)
- **Reward Strategy** (sources : or, objets…)
- **Composite Pattern** pour les quêtes principales → qui contiennent des sous-quêtes
- **Event Manager** pour notifier le joueur lors de l’accomplissement

---

## 🔹 Sous-quêtes (simples)

### ➤ **Créer une sous-quête**
```bash
python src/cli.py create-subquest <nom> <description> <difficulte>
```

Difficultés possibles : `facile` `moyen` `difficile` `epique`

**Exemple :**
```bash
python src/cli.py create-subquest "Tuer 5 gobelins" "La forêt est infestée" difficile
```

Génère automatiquement :

- XP via `DifficultyXpStrategy`
- Or via `GoldBasedOnDifficulty`
- Enregistrement dans le QuestManager

---

## 🔹 Quêtes principales (composites)

### ➤ **Créer une quête principale (COMPOSITE)**
Cette commande nécessite la liste des IDs de sous-quêtes.

```bash
python src/cli.py create-main-quest <nom> <description> <id1,id2,id3>
```

**Exemple :**
```bash
python src/cli.py create-main-quest "Protéger la vallée" "Regroupez les héros et éliminez la menace" 1,2,5
```

La quête composite est créée puis les sous-quêtes sont ajoutées via `add_subquest`.

XP et or sont générés via :

```python
FixedXpStrategy(500)
GoldBasedOnDifficulty(5)
```

---

## 🔹 Affichage / suivi des quêtes

### ➤ **Lister toutes les quêtes**
```bash
python src/cli.py list-quests
```

---

### ➤ **Accomplir une sous-quête**
```bash
python src/cli.py complete-quest <player_id> <quest_id>
```

Déclenche l'event :

- gain XP
- gain or
- appels EventManager

---

### ➤ **Voir les quêtes d’un joueur**
```bash
python src/cli.py player-quests <player_id>
```

---

# 🛠 Développement / Démo

### ➤ **Créer automatiquement une quête principale démo**
```bash
python src/cli.py create-demo-main-quest
```

Génère :

- 3 sous-quêtes
- une quête principale composite
- affichage de leur structure

---

# 🪓 Réinitialisation

### ➤ **Réinitialiser TOUTES les données**
```bash
python src/cli.py reset-data
```

Supprime :

- joueurs
- items
- quêtes

⚠️ Action irréversible.

---

# 📁 Structure du projet

```
src/
  cli.py
  event_manager.py
  quest/
    quest_base.py
    quest_types.py
    quest_factory.py
    quest_manager.py
  inventory/
    item.py
    inventory.py
  players/
    player.py
    player_manager.py
```

---

# ❓ Besoin d’ajouter / corriger des commandes ?

- Ajouter un système de niveaux ?
- Ajouter une classe de quêtes “Répétables” ?
- Ajouter des récompenses en objets ?
- Ajouter la persistance JSON/SQLite ?

Le CLI et le README peuvent être étendus selon ces besoins.
