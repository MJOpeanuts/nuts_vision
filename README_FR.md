# nuts_vision - Détection de Composants Électroniques & OCR

Système de vision par ordinateur pour l'analyse automatisée de cartes électroniques utilisant YOLOv8 et Tesseract OCR. Supporte maintenant la caméra Arducam 108MP avec focus motorisé pour la capture d'images.

> 🇬🇧 [English version](README.md) | 📷 [Guide Caméra](CAMERA_GUIDE_FR.md)

## Vue d'ensemble

Ce projet utilise la vision par ordinateur pour analyser des images de cartes électroniques, détecter et découper automatiquement les composants individuels (circuits intégrés, résistances, condensateurs, etc.), et extraire les numéros de pièce fabricant (MPN) via OCR. Le système est basé sur un modèle YOLO entraîné sur le dataset CompDetect (583 images, 16 classes de composants).

**Nouveauté:** Intégration complète de la caméra Arducam 108MP (réf: B0494C) pour capturer des photos haute résolution avec contrôle automatique du focus.

### Fonctionnalités Principales

- **🌐 Interface Web**: Interface Streamlit moderne avec visualiseur de base de données type Supabase
- **📷 Contrôle Caméra Arducam**: Support intégré pour la caméra Arducam 108MP avec focus motorisé
- **Détection de Composants**: Détection YOLOv8 de 16 types de composants
- **Prétraitement d'Image**: Flou gaussien et détection de contours pour améliorer la précision
- **Découpage Automatique**: Extraction des composants individuels depuis les images de cartes
- **Extraction de MPN**: Extraction OCR des numéros de pièce fabricant des circuits intégrés
- **Suivi en Base de Données**: Base de données PostgreSQL avec interface type Supabase
- **Export CSV**: Sauvegarde des MPNs extraits pour la gestion d'inventaire
- **Visualisation**: Génération de statistiques et visualisations des résultats

### Classes de Composants

Le modèle peut détecter les 16 types de composants suivants:
- IC (Circuit Intégré)
- LED
- Batterie
- Buzzer
- Condensateur
- Horloge
- Connecteur
- Diode
- Affichage
- Fusible
- Inductance
- Potentiomètre
- Relais
- Résistance
- Interrupteur
- Transistor

## Installation

### Prérequis

- Python 3.8 ou supérieur
- Tesseract OCR (pour l'extraction de MPN)

### Installer Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Téléchargez et installez depuis: https://github.com/UB-Mannheim/tesseract/wiki

### Installer les Dépendances Python

```bash
pip install -r requirements.txt
```

## Démarrage Rapide

### Option A: Interface Web (Recommandé)

L'interface web fournit une interface graphique moderne pour télécharger des images, lancer le traitement et visualiser les résultats dans une base de données de type Supabase.

```bash
# 1. Démarrer la base de données PostgreSQL
docker-compose up -d

# 2. Lancer l'interface web
./start_web.sh         # Linux/Mac
# ou
start_web.bat          # Windows
```

L'application s'ouvrira à `http://localhost:8501`

**Fonctionnalités de l'interface web:**
- 📤 Téléchargement et traitement d'images
- 🗄️ Visualiseur de base de données type Supabase
- 📊 Statistiques et analyses
- 📷 Aperçu des images et résultats

Pour plus de détails, consultez [INTERFACE_WEB.md](INTERFACE_WEB.md)

### Option C: Capture d'Images avec Caméra Arducam

nuts_vision supporte maintenant la caméra Arducam 108MP avec focus motorisé (référence B0494C).

**Via l'interface web:**

1. Lancez l'interface web : `streamlit run app.py`
2. Naviguez vers la page **📷 Contrôle Caméra**
3. Connectez-vous à la caméra
4. Réglez le focus (manuel ou automatique)
5. Capturez des photos haute résolution
6. Traitez les photos avec le pipeline de détection

**Via Python:**

```python
from src.camera_control import ArducamCamera
from src.pipeline import ComponentAnalysisPipeline

# Connexion à la caméra
camera = ArducamCamera(camera_index=0)
if camera.connect(width=1920, height=1080):
    # Réglage automatique du focus
    camera.auto_focus_scan()
    
    # Capture d'une photo
    photo_path = camera.capture_photo()
    
    # Traitement de la photo
    pipeline = ComponentAnalysisPipeline(model_path="runs/detect/component_detector/weights/best.pt")
    results = pipeline.process_image(photo_path)
    
    camera.disconnect()
```

📚 **Guides Supplémentaires:**
- [CAMERA.md](CAMERA.md) - Documentation complète de la caméra
- [ARDUCAM_OPTIMIZATION.md](ARDUCAM_OPTIMIZATION.md) - ⭐ **Optimisations pour images sombres et preview saccadé**
- [ARDUCAM_108MP_CONFIG.md](ARDUCAM_108MP_CONFIG.md) - Spécifications et configuration

### Option D: Ligne de Commande

#### 1. Entraîner le Modèle

D'abord, assurez-vous d'avoir le dataset prêt, puis entraînez le modèle YOLO:

```bash
python src/train.py --data data.yaml --epochs 100 --model-size n
```

Cela créera un modèle entraîné dans `runs/detect/component_detector/weights/best.pt`

#### 2. Exécuter le Pipeline Complet

Traitez des images de cartes électroniques et extrayez les informations des composants:

```bash
# Traiter une seule image
python src/pipeline.py --model runs/detect/component_detector/weights/best.pt --image path/to/board.jpg

# Traiter un répertoire d'images
python src/pipeline.py --model runs/detect/component_detector/weights/best.pt --image-dir path/to/images/
```

Cela va:
1. Détecter tous les composants dans l'image ou les images
2. Découper chaque composant en fichiers individuels
3. Extraire les MPNs des composants IC en utilisant l'OCR
4. Générer des visualisations et statistiques
5. Sauvegarder les résultats en fichiers CSV et JSON

#### 3. Test Simple avec une Photo

Pour un test rapide:

```bash
python test_simple.py --model runs/detect/component_detector/weights/best.pt --image ma_carte.jpg
```

## Utilisation Détaillée

### Entraînement

Entraîner un modèle YOLO pour la détection de composants:

```bash
python src/train.py \
  --data data.yaml \
  --model-size n \
  --epochs 100 \
  --batch 16 \
  --imgsz 640
```

**Arguments:**
- `--data`: Chemin vers le fichier de configuration data.yaml
- `--model-size`: Taille du modèle (n=nano, s=small, m=medium, l=large, x=xlarge)
- `--epochs`: Nombre d'époques d'entraînement
- `--batch`: Taille du batch
- `--imgsz`: Taille de l'image d'entrée

### Détection

Détecter les composants dans les images:

```bash
# Image unique
python src/detect.py --model path/to/best.pt --image board.jpg

# Traitement par lots
python src/detect.py --model path/to/best.pt --image-dir images/ --conf 0.3
```

**Arguments:**
- `--model`: Chemin vers le modèle YOLO entraîné
- `--image`: Chemin de l'image unique
- `--image-dir`: Répertoire d'images
- `--conf`: Seuil de confiance (par défaut: 0.25)
- `--no-preprocess`: Désactiver le prétraitement de l'image

### Découpage de Composants

Découper les composants détectés depuis les images:

```bash
python src/crop.py \
  --detection-file outputs/results/detections.json \
  --output-dir outputs/cropped_components \
  --padding 10
```

**Arguments:**
- `--detection-file`: Chemin vers detections.json depuis l'étape de détection
- `--output-dir`: Répertoire pour sauvegarder les composants découpés
- `--padding`: Padding autour des composants en pixels

### OCR / Extraction de MPN

Extraire les numéros de pièce fabricant depuis les images de composants:

```bash
python src/ocr.py \
  --image-dir outputs/cropped_components \
  --output-csv outputs/results/mpn_results.csv \
  --filter IC
```

**Arguments:**
- `--image-dir`: Répertoire contenant les images de composants découpés
- `--output-csv`: Chemin vers le fichier CSV de sortie
- `--filter`: Types de composants à traiter (par défaut: IC uniquement)

### Visualisation

Générer des statistiques et visualisations:

```bash
python src/visualize.py \
  --detection-file outputs/results/detections.json \
  --ocr-csv outputs/results/mpn_results.csv \
  --output-dir outputs/visualizations
```

## Structure du Projet

```
nuts_vision/
├── data.yaml                    # Configuration du dataset
├── requirements.txt             # Dépendances Python
├── README.md                    # Documentation (anglais)
├── README_FR.md                 # Cette documentation (français)
├── DEMARRAGE_RAPIDE.md         # Guide de démarrage rapide
├── test_simple.py              # Script de test simple
├── src/
│   ├── train.py                # Entraînement du modèle YOLO
│   ├── detect.py               # Détection de composants
│   ├── crop.py                 # Découpage de composants
│   ├── ocr.py                  # Extraction de MPN via OCR
│   ├── visualize.py            # Utilitaires de visualisation
│   └── pipeline.py             # Pipeline complet
├── outputs/
│   ├── results/                # Résultats de détection (JSON, CSV)
│   ├── cropped_components/     # Images de composants découpés
│   └── visualizations/         # Graphiques générés
└── models/                     # Modèles sauvegardés
```

## Fichiers de Sortie

Le pipeline génère plusieurs fichiers de sortie:

1. **detections.json**: Résultats de détection avec boîtes englobantes et scores de confiance
2. **mpn_results.csv**: MPNs extraits avec métadonnées
3. **mpn_results.json**: Résultats MPN au format JSON
4. **Images découpées**: Images de composants individuels dans `cropped_components/`
5. **Visualisations**: Graphiques statistiques dans `visualizations/`

### Exemple de Sortie CSV

```csv
image_path,component_type,raw_text,mpn
/path/to/IC_0.jpg,IC,LM358N,LM358N
/path/to/IC_1.jpg,IC,74HC595,74HC595
```

## Cas d'Usage

- **Contrôle Qualité**: Inspection automatisée des cartes électroniques assemblées
- **Gestion d'Inventaire**: Extraction des listes de composants depuis les images de cartes
- **Rétro-ingénierie**: Identification des composants sur les cartes existantes
- **Documentation**: Création de catalogues de composants depuis les images de cartes
- **Éducation**: Apprentissage sur les composants électroniques et la vision par ordinateur

## Informations sur le Dataset

Ce projet utilise le dataset **CompDetect v3** de Roboflow:
- **Images**: 583 images annotées
- **Classes**: 16 types de composants
- **Format**: YOLOv8
- **Licence**: CC BY 4.0

Pour plus d'informations, voir `README.roboflow.txt`

## Conseils de Performance

1. **Taille du Modèle**: Utilisez des modèles plus grands (m, l, x) pour une meilleure précision
2. **Seuil de Confiance**: Ajustez selon vos besoins (plus élevé = moins de faux positifs)
3. **Qualité d'Image**: Des images haute résolution donnent de meilleurs résultats OCR
4. **Prétraitement**: Activez le prétraitement pour les images bruitées
5. **Taille du Batch**: Réduisez si vous rencontrez des problèmes de mémoire

## Dépannage

### Tesseract introuvable
Assurez-vous que Tesseract OCR est installé et dans votre PATH. Testez avec:
```bash
tesseract --version
```

### CUDA out of memory
Réduisez la taille du batch ou utilisez un modèle plus petit:
```bash
python src/train.py --model-size n --batch 8
```

### Mauvais résultats OCR
- Assurez-vous que les images découpées ont une résolution suffisante
- Ajustez les paramètres de prétraitement
- Essayez différents modes PSM de Tesseract

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à soumettre des pull requests ou ouvrir des issues.

## Licence

Ce projet est sous licence selon les mêmes termes que le dataset CompDetect (CC BY 4.0).

## Remerciements

- YOLOv8 par Ultralytics
- Dataset CompDetect par Roboflow
- Tesseract OCR par Google

## Citation

Si vous utilisez ce projet dans votre recherche, veuillez citer:

```bibtex
@software{nuts_vision,
  title={nuts_vision: Détection de Composants Électroniques et OCR},
  author={contributeurs nuts_vision},
  year={2026},
  url={https://github.com/MJOpeanuts/nuts_vision}
}
```

---

Pour des instructions détaillées, consultez [DEMARRAGE_RAPIDE.md](DEMARRAGE_RAPIDE.md)
