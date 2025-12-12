# 🎮 Quest Manager - Application Web

Système de gestion de quêtes pour jeux RPG avec backend FastAPI et frontend web moderne.

---

## 🚀 Démarrage Rapide

```bash
# 1. Installation Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate     # Windows

pip install -r requirements.txt

# 2. Configuration
cp .env.example .env
# Éditez .env et changez SECRET_KEY

# 3. Lancement
python -m uvicorn app.main:app --reload
```

```bash
# 4. Lancement Frontend (nouveau terminal)
cd frontend
python -m http.server 3000
```

**Accès** : http://localhost:3000

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Démarrage en 5 minutes ⚡
- **[README_WEB.md](README_WEB.md)** - Documentation complète 📖
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migration depuis CLI 🔄
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Résolution de problèmes 🔧
- **[FILES_CHECKLIST.md](FILES_CHECKLIST.md)** - Liste des fichiers 📋

---

## 🎯 Fonctionnalités

✅ **Backend FastAPI**
- API REST complète
- Authentification JWT
- Multi-utilisateurs
- Décorateurs de quêtes (Decorator Pattern)
- Factory Pattern pour création de quêtes

✅ **Frontend Web**
- Dashboard joueur
- Dashboard admin
- Animations et notifications
- Design moderne et responsive

✅ **Système de Quêtes**
- Quêtes principales et secondaires
- Conditions (niveau, PNJ)
- Récompenses (XP, argent, objets)
- Progression et inventaire

---

## 🏗️ Architecture

```
quest-manager-web/
├── backend/          # API FastAPI
│   ├── app/
│   │   ├── routers/  # Routes API
│   │   ├── models/   # Modèles de données
│   │   ├── decorators/ # Pattern Decorator
│   │   └── quests/   # Logique quêtes
│   └── data/         # Fichiers JSON
│
└── frontend/         # Application web
    ├── *.html        # Pages
    ├── css/          # Styles
    └── js/           # Logic JavaScript
```

---

## 🛠️ Technologies

**Backend**
- FastAPI
- Python 3.8+
- JWT (python-jose)
- Bcrypt (passlib)

**Frontend**
- HTML5 / CSS3
- JavaScript (Vanilla)
- Fetch API

---

## 📦 Scripts Utiles

```bash
# Démarrer tout (Linux/Mac)
./start.sh

# Démarrer tout (Windows)
start.bat

# Arrêter (Linux/Mac)
./stop.sh

# Arrêter (Windows)
stop.bat
```

---

## 🧪 Test Rapide

1. **Créer un compte admin** : http://localhost:3000/register.html
2. **Créer une quête** : Dashboard admin → "Créer une quête"
3. **Créer un compte joueur**
4. **Accomplir la quête** → 🎊 Animation de succès !

---

## 📊 API Documentation

Une fois le backend lancé : **http://localhost:8000/docs**

---

## 🔐 Sécurité

- ⚠️ Changez `SECRET_KEY` dans `.env`
- ⚠️ Ne commitez JAMAIS `.env`
- ⚠️ En production : `DEBUG=False`

---

## 🐛 Problèmes ?

Consultez [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**🎮 Bonne gestion de quêtes !**