# Documentation Complète - Morpheus

## 📚 Table des Matières

### 🚀 [Démarrage Rapide](#démarrage-rapide)
### 🎨 [Thème UI & Design](#thème-ui--design)
### 🔌 [Simulateur CO₂](#simulateur-co₂)
### 🗄️ [Base de Données](#base-de-données)
### 🔐 [Authentification](#authentification)
### 📊 [API & WebSocket](#api--websocket)
### 🧪 [Tests](#tests)
### 📖 [Guides Détaillés](#guides-détaillés)

---

## Démarrage Rapide

### Installation
```bash
cd c:\Users\Zylow\Documents\NSI\PROJECT\Morpheus
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Lancer le serveur
```bash
python site/app.py
```
L'application démarre sur `http://localhost:5000`

### Structure du Projet
```
Morpheus/
├── site/
│   ├── app.py              # Application principale
│   ├── database.py         # Gestion BD
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css   # Styles (3000+ lignes)
│   │   └── js/
│   │       ├── main.js
│   │       └── utils.js
│   └── templates/
│       ├── base.html
│       ├── simulator.html
│       └── ...
├── app/
│   ├── co2_reader.py       # Lecteur CO₂
│   ├── datamanager.py
│   ├── co2_websocket_client.py
│   └── ...
└── requirements.txt
```

---

## 🎨 Thème UI & Design

### Système de Couleurs

#### Mode Sombre (Défaut)
- **Fond**: #0b0d12 (très sombre)
- **Cartes**: #141826 (gris sombre)
- **Texte primaire**: #e5e7eb (gris clair)
- **Accent**: #4db8ff (bleu clair)
- **Dégradé**: #0066cc → #0052a3 (bleu)

#### Mode Clair (Nouveau)
- **Fond**: #f8f9fa (gris très clair)
- **Cartes**: #ffffff (blanc)
- **Texte primaire**: #1a1f36 (gris sombre)
- **Accent**: #0066cc (bleu professionnel)
- **Boutons**: Bleu #0066cc

### Commutateur de Thème
Le bouton soleil/lune en haut à droite bascule entre:
- **Mode sombre**: Purple gradient moderne
- **Mode clair**: Material Design professionnel

### Fonctionnalités Material Design
- **Élévation**: Ombres à plusieurs niveaux (2px, 4px, 8px)
- **Transitions**: Animations fluides (0.2s ease)
- **États interactifs**: Hover + Focus + Active
- **Contraste**: Norme WCAG AAA/AA respectée

### Fichiers CSS
- `static/css/style.css` - 2870+ lignes
  - Thème sombre complet
  - Mode clair complet avec Material Design
  - Responsive design
  - Animations et transitions

---

## 🔌 Simulateur CO₂

### Page du Simulateur
- URL: `/simulator`
- Permet de tester différents scénarios
- Envoie les données en temps réel via WebSocket
- Stocke les données dans la base de données

### Scénarios Disponibles

1. **Normal** 🏢
   - Variations mineures de CO₂
   - CO₂ stable autour de 600 ppm
   - Oscillations naturelles

2. **Heures de Bureau** 👥
   - Personnes présentes
   - CO₂ monte progressivement
   - Augmentation graduelle due à l'occupation

3. **Sommeil** 🌙
   - Peu de personnes
   - CO₂ très stable et bas
   - Conditions minimales d'occupation

4. **Ventilation Active** 💨
   - Système de ventilation en cours
   - CO₂ baisse rapidement
   - Renouvellement d'air efficace

5. **Anomalie Capteur** ⚠️
   - Anomalie de capteur
   - Pics aléatoires
   - Dérive progressive ou interruptions

### Configuration du Simulateur
```javascript
// Durée: en minutes (0 = infini)
// Scénario: "normal", "office_hours", "sleep", "ventilation_active", "anomaly"
```

### Fonctionnalités
- Actualisation en temps réel (2 sec)
- Durée configurable par scénario
- Réinitialisation possible
- Intégration avec page "En Direct"
- Données persistantes en BD

---

## 🗄️ Base de Données

### Tables Principales

#### `co2_data`
```sql
id: INTEGER PRIMARY KEY
timestamp: DATETIME
co2_ppm: FLOAT
temperature: FLOAT
humidity: FLOAT
source: VARCHAR (simulator/real)
simulator_scenario: VARCHAR (scénario utilisé)
```

#### `users`
```sql
id: INTEGER PRIMARY KEY
username: VARCHAR UNIQUE
email: VARCHAR UNIQUE
password_hash: VARCHAR
is_admin: BOOLEAN
verified: BOOLEAN
created_at: DATETIME
```

#### `admin_settings`
```sql
id: INTEGER PRIMARY KEY
user_id: INTEGER FK
setting_name: VARCHAR
setting_value: VARCHAR
```

### Migration BD
```bash
python site/update_db.py
```

### Sauvegarde des Données
```bash
python site/check_db.py
```

---

## 🔐 Authentification

### Système d'Authentification
- Connexion/déconnexion
- Inscription utilisateurs
- Récupération mot de passe
- Vérification email
- Rôles: Utilisateur normal / Admin

### Fonctionnalités
- **Connexion**: Login avec username/email
- **Inscription**: Création compte + vérification email
- **Mot de passe oublié**: Réinitialisation sécurisée
- **Authentification JWT**: Tokens sécurisés
- **Permissions**: Accès admin restreint

### Pages d'Authentification
- `/login` - Formulaire de connexion
- `/register` - Inscription
- `/forgot_password` - Réinitialisation
- `/reset_password/<token>` - Définir nouveau mot de passe
- `/verify_email/<token>` - Vérifier email

---

## 📊 API & WebSocket

### Points de Terminaison API

#### CO₂ Data
```
GET /api/co2/latest         - Dernière mesure
GET /api/co2/range          - Plage de dates
GET /api/co2/daily          - Données quotidiennes
GET /api/co2/hourly         - Données horaires
```

#### Simulateur
```
GET /api/simulator/status   - État actuel
POST /api/simulator/start   - Démarrer scénario
POST /api/simulator/stop    - Arrêter
POST /api/simulator/reset   - Réinitialiser
```

#### Utilisateurs
```
GET /api/user/profile       - Profil utilisateur
POST /api/user/update       - Mettre à jour profil
POST /api/user/password     - Changer mot de passe
```

### WebSocket

**Connexion**:
```javascript
const ws = new WebSocket('ws://localhost:5000/ws/live');
```

**Messages reçus**:
```json
{
  "type": "co2_update",
  "data": {
    "co2_ppm": 600,
    "temperature": 22.0,
    "humidity": 45.0,
    "timestamp": "2026-01-04 14:30:00"
  }
}
```

**Utilisation**: 
- Page "En Direct" reçoit updates temps réel
- Graphiques se mettent à jour automatiquement
- Tableaux de bord synchronisés

---

## 🧪 Tests

### Scripts de Test
```bash
# Test complet authentification
python site/test_auth.py

# Test flux de connexion
python site/test_login_flow.py

# Vérifier base de données
python site/verify_quick.py

# Test admin
python site/test_admin_password.py
```

### Tests Manuels
1. Ouvrir http://localhost:5000
2. Tester inscription/connexion
3. Tester simulateur CO₂
4. Tester changement de thème
5. Vérifier données en temps réel

---

## 📖 Guides Détaillés

### Guide du Thème UI
- Comment utiliser le commutateur de thème
- Système de couleurs Material Design
- Responsive design
- Accessibilité WCAG

### Guide du Simulateur
- Lancer et configurer scénarios
- Interpréter les résultats
- Données exportées
- Intégration avec tableaux de bord

### Guide d'Administration
- Accès panel admin
- Gestion utilisateurs
- Paramètres d'application
- Sauvegarde/restauration données

### Guide d'Intégration
- Configuration WebSocket
- Appels API
- Format JSON
- Authentification API

---

## 🔧 Configuration

### Fichier `.env` (optionnel)
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///morpheus.db
```

### Variables d'Environnement
- `FLASK_ENV`: development/production
- `DEBUG`: True/False
- `SECRET_KEY`: Clé secrète app
- `DATABASE_URL`: Chemin BD

---

## 📞 Support & Dépannage

### Problèmes Communs

**Le thème ne change pas?**
- Actualiser la page (Ctrl+F5)
- Vider le cache navigateur
- Vérifier console pour erreurs

**Simulateur ne démarre pas?**
- Vérifier BD créée
- Vérifier permissions fichiers
- Regarder logs serveur

**WebSocket non connecté?**
- Vérifier serveur actif
- Vérifier port 5000 libre
- Vérifier pare-feu

**Authentification échouée?**
- Vérifier nom d'utilisateur/email
- Vérifier mot de passe
- Vérifier BD utilisateurs

---

## 📝 Changelog Récent

### Version Actuelle (Jan 2026)
- ✅ Thème Material Design Light complet
- ✅ Simulateur CO₂ fonctionnel
- ✅ Authentification sécurisée
- ✅ WebSocket temps réel
- ✅ Documentation complète

### Améliorations Récentes
- Correction sélecteurs CSS variables
- Ajout Material Design light theme
- Amélioration responsive design
- Optimisation performances

---

## 📚 Ressources

- **Flask**: https://flask.palletsprojects.com/
- **Material Design**: https://material.io/design/
- **WebSocket**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- **SQLite**: https://www.sqlite.org/

---

## 💡 Prochaines Étapes

1. ✅ Thème UI complet (FAIT)
2. ✅ Simulateur CO₂ (FAIT)
3. ✅ Authentification (FAIT)
4. ✅ Mode clair Material Design (FAIT)
5. 📋 Optimisation performances
6. 📋 Tests supplémentaires
7. 📋 Déploiement production

---

**Dernière mise à jour**: 4 Janvier 2026
**Version**: 1.0
**Status**: ✅ Stable et Fonctionnel

Pour plus d'informations, consultez les sections détaillées ci-dessus.
