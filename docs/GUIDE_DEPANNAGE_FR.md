# 🔧 Guide de Dépannage - Morpheus

## ⚡ Problèmes Communs et Solutions

---

## 🎨 Problèmes de Thème

### Le thème clair ne change pas
**Symptôme**: Cliquer sur le bouton soleil/lune ne change rien

**Solutions**:
1. **Vider le cache navigateur**
   - Appuyer sur `Ctrl+Shift+R` (Hard refresh)
   - Ou `Ctrl+Shift+Suppr` (Effacer données)

2. **Vérifier la console navigateur**
   - Appuyer sur `F12`
   - Onglet "Console"
   - Chercher les erreurs rouge

3. **Redémarrer le navigateur**
   - Fermer complètement
   - Rouvrir et tester

4. **Vérifier que CSS charge**
   - `F12` → Onglet "Éléments"
   - Chercher `<style>` dans `<head>`
   - Vérifier pas d'erreurs

**Si ça persiste**: Consulter section "En cas de problème persistent"

---

### Le thème clair est mal stylisé
**Symptôme**: Couleurs bizarres, texte illisible

**Solutions**:
1. **Rafraîchir la page**
   - `Ctrl+R` ou `F5`

2. **Vérifier CSS chargé correctement**
   ```
   F12 → Application → Stylesheets
   Vérifier style.css présent et chargé
   ```

3. **Vérifier les variables CSS**
   - `F12` → Console
   - Taper: `getComputedStyle(document.documentElement).getPropertyValue('--bg')`
   - Doit retourner couleur light mode ou dark mode

---

### Contraste trop faible (texte illisible)
**Symptôme**: Texte trop clair ou trop sombre

**Solutions**:
1. **Mode sombre**: Cliquer sur soleil (mode clair)
2. **Mode clair**: Cliquer sur lune (mode sombre)
3. **Augmenter zoom navigateur** `Ctrl++`

---

## 🔌 Problèmes de Simulateur

### Le simulateur ne démarre pas
**Symptôme**: Bouton "Activer" ne fait rien

**Solutions**:
1. **Vérifier le serveur actif**
   ```bash
   # Dans terminal, vérifier:
   # "Running on http://localhost:5000"
   ```

2. **Vérifier la base de données**
   ```bash
   python site/check_db.py
   ```

3. **Regarde les logs serveur**
   - Terminal Flask doit afficher messages
   - Chercher les erreurs

4. **Recharger la page**
   - `Ctrl+R`
   - Essayer un autre scénario

### Simulateur démarre mais pas de données
**Symptôme**: Page "En Direct" vide

**Solutions**:
1. **Vérifier WebSocket**
   - `F12` → Onglet "Réseau"
   - Chercher "ws://" 
   - Doit montrer vert (connecté)

2. **Redémarrer simulateur**
   - Cliquer "Réinitialiser"
   - Relancer le scénario

3. **Vérifier serveur actif**
   - Regarder terminal Flask
   - Doit montrer messages WebSocket

### Erreur "Impossible de charger état"
**Symptôme**: Message erreur au lancement

**Solutions**:
1. **Vérifier BD**
   ```bash
   python site/verify_quick.py
   ```

2. **Créer tables BD**
   ```bash
   python site/update_db.py
   ```

3. **Rafraîchir page**
   - `Ctrl+R`

---

## 🔐 Problèmes d'Authentification

### Impossible de se connecter
**Symptôme**: "Nom d'utilisateur ou mot de passe incorrect"

**Solutions**:
1. **Vérifier identifiants**
   - Username/Email correct?
   - Mot de passe correct?

2. **Vérifier BD utilisateurs**
   ```bash
   python site/check_db.py
   ```

3. **Réinitialiser mot de passe**
   - Cliquer "Mot de passe oublié"
   - Suivre email

4. **Recréer compte**
   - Cliquer "S'inscrire"
   - Entrer infos nouvelles

### Email de vérification ne reçoit pas
**Symptôme**: Email n'arrive pas

**Solutions**:
1. **Vérifier spam/indésirables**
   - Regarder dossier spam

2. **Email correct?**
   - Vérifier l'adresse email entrée

3. **Serveur email**
   - Vérifier config SMTP dans app.py
   - Vérifier serveur email actif

4. **Manquer de temps**
   - Attendre quelques minutes
   - Vérifier nouveau les emails

### Impossible d'accéder à Admin
**Symptôme**: Pas d'onglet Admin

**Solutions**:
1. **Vérifier vous êtes admin**
   ```bash
   python site/promote_admin.py
   ```

2. **Déconnecter/Reconnecter**
   - Logout
   - Login à nouveau

3. **Vérifier BD**
   ```bash
   python site/check_admin.py
   ```

---

## 🗄️ Problèmes de Base de Données

### "Database locked" erreur
**Symptôme**: Erreur lors de sauvegarde données

**Solutions**:
1. **Fermer autres connexions**
   - Fermer autres onglets
   - Arrêter serveur (Ctrl+C)
   - Redémarrer

2. **Vérifier permissions fichier**
   - Faire clic-droit sur fichier .db
   - Propriétés → Sécurité
   - S'assurer permissions lecture/écriture

3. **Recréer BD**
   ```bash
   # Supprimer ancienne BD
   del site/data/morpheus.db
   # Créer nouvelle
   python site/update_db.py
   ```

### Données perdues
**Symptôme**: Données de CO₂ disparues

**Solutions**:
1. **Vérifier BD existe**
   ```bash
   python site/check_db.py
   ```

2. **Chercher backup** (si existe)
   - Dossier "data/"
   - Chercher fichiers .db anciens

3. **Restaurer depuis backup**
   - Copier ancien .db
   - Relancer serveur

---

## 🌐 Problèmes de Connectivité

### Port 5000 déjà utilisé
**Symptôme**: "Address already in use"

**Solutions**:
1. **Trouver process sur port 5000**
   ```powershell
   netstat -ano | findstr :5000
   ```

2. **Tuer le process**
   ```powershell
   taskkill /PID [PID] /F
   ```

3. **Ou changer le port**
   - Éditer `app.py`
   - Changer `app.run(port=5000)` → `app.run(port=5001)`

### Impossible d'accéder à localhost:5000
**Symptôme**: "Impossible de joindre le serveur"

**Solutions**:
1. **Vérifier serveur actif**
   - Terminal doit afficher: "Running on http://localhost:5000"

2. **Vérifier pare-feu**
   - Permettre Python
   - Permettre port 5000

3. **Essayer URL différente**
   - `127.0.0.1:5000` au lieu de `localhost:5000`

4. **Redémarrer serveur**
   - `Ctrl+C` pour arrêter
   - Relancer `python site/app.py`

---

## 📊 Problèmes de Données

### Graphiques ne montrent rien
**Symptôme**: Pages "En Direct" / "Tableau de Bord" vides

**Solutions**:
1. **Lancer simulateur**
   - Aller à `/simulator`
   - Démarrer un scénario
   - Attendre quelques secondes

2. **Vérifier données en BD**
   ```bash
   python site/verify_quick.py
   ```

3. **Rafraîchir page**
   - `Ctrl+R`
   - Attendre données se charger

### Données anciennes (pas mise à jour)
**Symptôme**: Données figées, pas de changement

**Solutions**:
1. **Vérifier simulateur actif**
   - Aller à `/simulator`
   - Vérifier scénario actif

2. **Vérifier WebSocket**
   - `F12` → Réseau
   - Chercher WebSocket actif

3. **Redémarrer navigateur**
   - Fermer/Rouvrir
   - Relancer page

---

## 🐛 Problèmes Techniques

### Erreur Python/Serveur
**Symptôme**: Code erreur dans terminal

**Solutions**:
1. **Lire le message d'erreur**
   - Regarder la ligne d'erreur
   - Chercher le fichier/numéro ligne

2. **Vérifier imports**
   ```bash
   python -m py_compile app.py
   ```

3. **Vérifier dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Vérifier Python version**
   ```bash
   python --version
   # Doit être Python 3.8+
   ```

### Import manquant
**Symptôme**: "ModuleNotFoundError: No module named..."

**Solutions**:
1. **Installer le module**
   ```bash
   pip install [nom-module]
   ```

2. **Réinstaller tous les modules**
   ```bash
   pip install -r requirements.txt
   ```

3. **Utiliser le bon environnement virtuel**
   ```bash
   .\venv\Scripts\activate
   ```

---

## 📋 Checklist de Dépannage

### Avant d'appeler à l'aide, vérifier:

- [ ] Actualiser page (Ctrl+R)
- [ ] Hard refresh (Ctrl+Shift+R)
- [ ] Vider cache
- [ ] Fermer/Rouvrir navigateur
- [ ] Redémarrer serveur
- [ ] Vérifier console (F12)
- [ ] Vérifier terminal serveur
- [ ] Vérifier BD
- [ ] Vérifier port 5000 libre
- [ ] Vérifier internet connecté

Si tout ci-dessus ✅ et problème persiste:

---

## 🆘 En Cas de Problème Persistent

### Recréer l'environnement
```bash
# Arrêter serveur (Ctrl+C)

# Supprimer environnement
rmdir /s /q venv

# Créer nouvel environnement
python -m venv venv
.\venv\Scripts\activate

# Réinstaller
pip install -r requirements.txt

# Recréer BD
del site/data/morpheus.db
python site/update_db.py

# Relancer
python site/app.py
```

### Vérifier l'installation complète
```bash
# Tester imports
python -c "import flask; print('Flask OK')"
python -c "import flask_sqlalchemy; print('SQLAlchemy OK')"
python -c "import flask_login; print('Login OK')"

# Vérifier BD
python site/check_db.py

# Vérifier app
python site/app.py
```

### Logs détaillés
```bash
# Activer mode debug
# Dans app.py, ajouter:
# app.config['DEBUG'] = True
# app.logger.setLevel(logging.DEBUG)

# Relancer
python site/app.py
```

---

## 📞 Informations à Fournir

Si problème persiste, noter:

1. **Version Python**
   ```bash
   python --version
   ```

2. **Message d'erreur exact** (copier/coller)

3. **Étapes pour reproduire**
   - Quoi faire exactement pour voir l'erreur

4. **Logs du serveur**
   - Copier ce que affiche le terminal Flask

5. **Logs du navigateur**
   - F12 → Console → Copier les messages rouge

6. **Système d'exploitation**
   - Windows / Linux / Mac

7. **Navigateur utilisé**
   - Chrome / Firefox / Safari / Edge

---

## 🎯 Ressources Utiles

- **Documentation**: DOCUMENTATION_FR.md
- **Flask Docs**: https://flask.palletsprojects.com/
- **SQLite Docs**: https://www.sqlite.org/
- **WebSocket**: https://developer.mozilla.org/fr/docs/Web/API/WebSocket

---

**Dernière mise à jour**: 4 Janvier 2026
**Version**: 1.0
**Status**: ✅ À jour

