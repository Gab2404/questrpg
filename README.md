# 🎮 Quest Manager - Système de Gestion de Quêtes

Projet de démonstration du **Design Pattern Decorator** appliqué à un système de quêtes pour jeux vidéo RPG.

---

## 📋 Installation

### Prérequis
- Python 3.8+
- pip

### Étape unique

```bash
pip install -r requirements.txt 
```

C'est tout ! La structure de dossiers est déjà en place.

---

## 💻 Commandes - Interface Joueur

### Afficher le statut du joueur
```bash
python -m cli.quest_manager status
```
Affiche : niveau, XP, argent, inventaire, quêtes complétées

### Lister toutes les quêtes
```bash
python -m cli.quest_manager list-quests
```
Affiche toutes les quêtes avec leur statut (✅ terminée / 🆕 disponible)

### Parler au PNJ
```bash
python -m cli.quest_manager talk-npc
```
Simule une conversation avec un PNJ (débloque les quêtes nécessitant une interaction)

### Accomplir une quête
```bash
python -m cli.quest_manager do-quest <numéro>
```
**Exemple** : `python -m cli.quest_manager do-quest 1`

Tente d'accomplir la quête. Vérifie automatiquement :
- Si la quête est déjà terminée
- Si le niveau est suffisant
- Si le PNJ a été contacté (si requis)

### Modifier le niveau (triche)
```bash
python -m cli.quest_manager cheat-level <niveau>
```
**Exemple** : `python -m cli.quest_manager cheat-level 10`

### Réinitialiser la sauvegarde
```bash
python -m cli.quest_manager reset-save
```
Supprime `data/save.json` pour recommencer à zéro

---

## 🛠️ Commandes - Interface Admin

### Lister toutes les quêtes
```bash
python -m cli.quest_admin list
```
Affiche un tableau : ID | Titre | Type | XP

### Créer une nouvelle quête
```bash
python -m cli.quest_admin create
```
Mode interactif pour créer une quête :
1. Titre
2. Description
3. XP de base
4. Type (Principale/Secondaire)
5. Configuration des décorateurs (optionnel)

### Modifier une quête existante
```bash
python -m cli.quest_admin modify <id>
```
**Exemple** : `python -m cli.quest_admin modify 1`

Menu interactif pour modifier :
- Titre
- Description
- XP de base
- Type
- Décorateurs (conditions/récompenses)

### Supprimer une quête
```bash
python -m cli.quest_admin delete <id>
```
**Exemple** : `python -m cli.quest_admin delete 5`

### Réparer les IDs
```bash
python -m cli.quest_admin fix-ids
```
Réattribue des IDs séquentiels (1, 2, 3...) en cas de doublons

---

## 🎨 Types de Décorateurs

### Conditions (Requirements)
- **level_req** : Niveau minimum requis
- **npc_req** : Avoir parlé à un PNJ

### Récompenses (Rewards)
- **money_reward** : Pièces d'or
- **item_reward** : Objet ajouté à l'inventaire

---

## 📚 Exemples d'Utilisation

### Scénario 1 : Commencer le jeu

```bash
# Voir le statut initial
python -m cli.quest_manager status

# Lister les quêtes
python -m cli.quest_manager list-quests

# Tenter la quête 1 (niveau 1 requis)
python -m cli.quest_manager do-quest 1
```

### Scénario 2 : Quête avec condition PNJ

```bash
# Tenter une quête nécessitant un PNJ
python -m cli.quest_manager do-quest 2
# ❌ Vous devez d'abord parler au PNJ !

# Parler au PNJ
python -m cli.quest_manager talk-npc

# Réessayer
python -m cli.quest_manager do-quest 2
# ✅ Succès !
```

### Scénario 3 : Quête de haut niveau

```bash
# Tenter une quête niveau 10
python -m cli.quest_manager do-quest 3
# ❌ Niveau insuffisant. Requis: 10, Actuel: 1

# Tricher pour passer niveau 10
python -m cli.quest_manager cheat-level 10

# Réessayer
python -m cli.quest_manager do-quest 3
# ✅ Succès ! + récompenses
```

### Scénario 4 : Créer une quête complète

```bash
# Lancer la création
python -m cli.quest_admin create

# Suivre les instructions :
📝 Titre de la quête: Tuer 10 Gobelins
📖 Description: Éliminez 10 gobelins dans la forêt
⭐ XP de base: 100
🎯 Quête Principale ? [Y/n]: y
⚙️  Voulez-vous configurer les conditions/récompenses maintenant ? [Y/n]: y

# Dans le menu décorateurs :
A. Ajouter un décorateur
1. Condition : Niveau requis
Niveau minimum: 5

A. Ajouter un décorateur
3. Récompense : Argent
Montant en pièces: 500

R. Retour
6. Sauvegarder et Quitter
```

---

## 📁 Structure du Projet

```
quest_manager_project/
├── models/
│   ├── __init__.py
│   ├── player.py
│   └── quest_interfaces.py
├── quests/
│   ├── __init__.py
│   ├── base_quest.py
│   └── quest_factory.py
├── decorators/
│   ├── __init__.py
│   ├── quest_decorator.py
│   ├── requirements.py
│   └── rewards.py
├── storage/
│   ├── __init__.py
│   ├── player_storage.py
│   └── quest_storage.py
├── cli/
│   ├── __init__.py
│   ├── quest_admin.py
│   └── quest_manager.py
├── data/
│   ├── quests_db.json
│   └── save.json
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 📄 Format JSON

### Structure d'une quête

```json
{
    "id": 1,
    "title": "Tuer 10 Gobelins",
    "description": "Éliminez 10 gobelins dans la forêt sombre",
    "base_xp": 100,
    "type": "PRIMARY",
    "decorators": [
        {
            "type": "level_req",
            "value": 5
        },
        {
            "type": "npc_req",
            "value": "Garde du village"
        },
        {
            "type": "money_reward",
            "value": 500
        },
        {
            "type": "item_reward",
            "value": "Épée en fer"
        }
    ]
}
```

### Structure de la sauvegarde

```json
{
    "name": "Héros",
    "level": 5,
    "xp": 250,
    "money": 1500,
    "inventory": ["Épée en fer", "Potion de vie"],
    "spoken_to_npc": true,
    "completed_quests": [1, 2, 3]
}
```

---
