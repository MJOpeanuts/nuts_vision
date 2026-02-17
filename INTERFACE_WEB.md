# Interface Web nuts_vision

## 🌐 Vue d'ensemble

L'interface web de **nuts_vision** fournit une interface graphique moderne et intuitive pour analyser des cartes électroniques et gérer les résultats dans une base de données de type Supabase.

## ✨ Fonctionnalités

### 1. 📤 Téléchargement et Traitement d'Images
- Téléchargez une ou plusieurs images de cartes électroniques (PCB)
- Configuration du modèle YOLO et du seuil de confiance
- Traitement automatique avec détection, découpage et OCR
- Aperçu des images téléchargées
- Suivi en temps réel de la progression

### 2. 🗄️ Visualiseur de Base de Données (Type Supabase)
Vue de type Supabase de toutes les tables de la base de données :

- **📸 Images Input** : Toutes les images téléchargées/traitées
- **🔄 Jobs Log** : Historique de tous les travaux de détection
- **🎯 Detections** : Résultats de détection avec boîtes englobantes
- **✂️ Cropped ICs** : Images découpées des circuits intégrés
- **📝 OCR Results** : Résultats d'extraction OCR avec MPNs

Fonctionnalités :
- Rafraîchissement en temps réel
- Filtrage par job
- Affichage des statistiques détaillées
- Export des données

### 3. 📊 Statistiques et Analyses
- Vue d'ensemble avec métriques clés
- Distribution des composants détectés
- Taux de réussite de l'extraction MPN
- Graphiques et visualisations interactifs
- Historique des travaux récents

### 4. ℹ️ Informations Système
- État de la connexion à la base de données
- Informations sur l'environnement
- Documentation et aide
- Statut du modèle YOLO

## 🚀 Démarrage Rapide

### Prérequis

1. **Python 3.8+** installé
2. **PostgreSQL** en cours d'exécution (via Docker ou installation locale)
3. **Tesseract OCR** installé sur le système

### Installation

#### Option 1 : Utilisation de Docker (Recommandé)

```bash
# 1. Démarrer la base de données PostgreSQL
docker-compose up -d

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Lancer l'interface web
./start_web.sh         # Linux/Mac
# ou
start_web.bat          # Windows
```

#### Option 2 : Installation Manuelle

```bash
# 1. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer la base de données PostgreSQL
# Créer la base de données et l'utilisateur
psql -U postgres
CREATE DATABASE nuts_vision;
CREATE USER nuts_user WITH PASSWORD 'nuts_password';
GRANT ALL PRIVILEGES ON DATABASE nuts_vision TO nuts_user;
\q

# Initialiser le schéma
psql -U nuts_user -d nuts_vision -f database/init.sql

# 4. Configurer les variables d'environnement (optionnel)
cp .env.example .env
# Éditer .env avec vos paramètres

# 5. Lancer l'application
streamlit run app.py
```

### Premier Lancement

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse :
```
http://localhost:8501
```

## 📖 Guide d'Utilisation

### 1. Page d'Accueil (🏠 Home)

La page d'accueil affiche :
- Vue d'ensemble du système
- Liste des composants détectables
- Statistiques rapides (si la base de données est connectée)
- Guide de démarrage rapide

### 2. Téléchargement et Traitement (📤 Upload & Process)

#### Étape 1 : Configuration du Modèle
- **Chemin du Modèle** : Indiquez le chemin vers votre modèle YOLO entraîné
  - Par défaut : `runs/detect/component_detector/weights/best.pt`
- **Seuil de Confiance** : Ajustez entre 0.1 et 0.9 (recommandé : 0.25)

#### Étape 2 : Téléchargement d'Images
- Cliquez sur "Browse files" ou glissez-déposez vos images
- Formats acceptés : JPG, JPEG, PNG
- Plusieurs images peuvent être téléchargées en une fois

#### Étape 3 : Options de Traitement
- **Extract MPNs (OCR)** : Active l'extraction des numéros de pièce
- **Log to Database** : Enregistre les résultats dans la base de données
- **Create Visualizations** : Génère des graphiques et visualisations

#### Étape 4 : Lancer le Traitement
- Cliquez sur "🚀 Start Processing"
- Suivez la progression en temps réel
- Consultez le résumé des résultats

### 3. Visualiseur de Base de Données (🗄️ Database Viewer)

#### Vue des Tables

**📸 Images Input**
- Affiche toutes les images téléchargées
- Colonnes : `image_id`, `file_name`, `file_path`, `upload_at`, `format`
- Permet de tracer l'historique complet des images

**🔄 Jobs Log**
- Liste tous les travaux de détection exécutés
- Affiche le statut, les timestamps, le modèle utilisé
- Nombre de détections par job
- Détails détaillés pour chaque job sélectionné

**🎯 Detections**
- Tous les composants détectés avec leurs coordonnées
- Filtrage par job possible
- Distribution des types de composants
- Scores de confiance

**✂️ Cropped ICs**
- Images découpées des circuits intégrés
- Liens vers les fichiers découpés
- Association avec les détections

**📝 OCR Results**
- Résultats de l'extraction OCR
- MPNs extraits (numéros de pièce fabricant)
- Angle de rotation utilisé
- Scores de confiance OCR
- Taux de réussite

#### Fonctionnalités

- **Rafraîchissement** : Bouton "🔄 Refresh" pour actualiser les données
- **Filtrage** : Filtrer par job ID dans certaines vues
- **Statistiques** : Métriques et graphiques intégrés
- **Export** : Copier ou exporter les données affichées

### 4. Statistiques (📊 Statistics)

#### Métriques d'Aperçu
- Total d'images traitées
- Nombre de jobs exécutés
- Total de détections
- Résultats OCR
- Taux de réussite MPN

#### Distribution des Composants
- Graphique à barres des types de composants
- Tableau de comptage détaillé
- Visualisation interactive

#### Travaux Récents
- Liste des 10 derniers travaux
- Informations sur le fichier traité
- Nombre de détections

### 5. À Propos (ℹ️ About)

- Informations sur le système
- Technologies utilisées
- Schéma de base de données
- Documentation
- État du système

## ⚙️ Configuration

### Variables d'Environnement

Créez un fichier `.env` à la racine du projet :

```bash
# Configuration de la Base de Données
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nuts_vision
DB_USER=nuts_user
DB_PASSWORD=nuts_password
```

### Configuration de Streamlit

Créez un fichier `.streamlit/config.toml` pour personnaliser l'interface :

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
address = "localhost"
maxUploadSize = 200
```

## 🔍 Dépannage

### La Base de Données ne se Connecte Pas

**Vérifications :**
1. PostgreSQL est-il en cours d'exécution ?
   ```bash
   docker-compose ps  # Pour Docker
   # ou
   sudo systemctl status postgresql  # Pour installation système
   ```

2. Les identifiants sont-ils corrects ?
   - Vérifiez vos variables d'environnement
   - Testez la connexion manuellement :
   ```bash
   psql -h localhost -U nuts_user -d nuts_vision
   ```

3. Le schéma est-il initialisé ?
   ```bash
   psql -U nuts_user -d nuts_vision -f database/init.sql
   ```

### Le Modèle n'est pas Trouvé

**Solution :**
1. Vérifiez que le modèle YOLO est entraîné :
   ```bash
   ls runs/detect/component_detector/weights/best.pt
   ```

2. Si non, entraînez le modèle :
   ```bash
   python src/train.py --data data.yaml --epochs 100 --model-size n
   ```

3. Ou spécifiez un chemin personnalisé dans l'interface

### Erreur lors du Téléchargement

**Vérifications :**
- La taille du fichier est-elle < 200 MB ?
- Le format est-il supporté (JPG, JPEG, PNG) ?
- Le dossier `uploads/` est-il accessible en écriture ?

### L'OCR ne Fonctionne Pas

**Vérifications :**
1. Tesseract est-il installé ?
   ```bash
   tesseract --version
   ```

2. Installation si nécessaire :
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # macOS
   brew install tesseract
   
   # Windows
   # Télécharger depuis https://github.com/UB-Mannheim/tesseract/wiki
   ```

### Port 8501 Déjà Utilisé

**Solution :**
```bash
# Utiliser un port différent
streamlit run app.py --server.port 8502
```

## 📊 Exemples d'Utilisation

### Traitement d'une Image Unique

1. Aller à "📤 Upload & Process"
2. Télécharger une image de PCB
3. Conserver les paramètres par défaut
4. Cliquer sur "🚀 Start Processing"
5. Attendre la fin du traitement
6. Consulter les résultats dans "🗄️ Database Viewer"

### Traitement par Lots

1. Télécharger plusieurs images en une fois
2. Activer toutes les options de traitement
3. Lancer le traitement
4. Visualiser les statistiques dans "📊 Statistics"

### Consultation de l'Historique

1. Aller à "🗄️ Database Viewer"
2. Sélectionner "🔄 Jobs Log"
3. Choisir un job pour voir les détails
4. Explorer les détections associées

### Export de Données

1. Afficher une table dans "🗄️ Database Viewer"
2. Utiliser les options d'export de Streamlit (coin supérieur droit du tableau)
3. Télécharger au format CSV

## 🔐 Sécurité

**⚠️ Important pour la Production :**

1. **Changez les mots de passe par défaut** dans `.env` et `docker-compose.yml`
2. **Utilisez HTTPS** pour les déploiements publics
3. **Limitez l'accès** à la base de données
4. **Activez l'authentification** Streamlit si nécessaire
5. **Sauvegardes régulières** de la base de données :
   ```bash
   docker exec nuts_vision_db pg_dump -U nuts_user nuts_vision > backup.sql
   ```

## 📚 Ressources Supplémentaires

- [Documentation Streamlit](https://docs.streamlit.io/)
- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [Documentation YOLOv8](https://docs.ultralytics.com/)
- [Documentation Tesseract](https://github.com/tesseract-ocr/tesseract)

## 🆘 Support

Pour toute question ou problème :
1. Consultez la documentation
2. Vérifiez les issues GitHub existantes
3. Créez une nouvelle issue sur GitHub

---

**Version** : 1.0.0  
**Dernière mise à jour** : 2026-02-17
