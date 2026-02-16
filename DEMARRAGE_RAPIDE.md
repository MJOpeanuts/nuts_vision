# Guide de Démarrage Rapide - nuts_vision

Ce guide vous aidera à installer et utiliser nuts_vision pour détecter des composants électroniques et extraire les numéros de pièce fabricant (MPN).

## Prérequis

Avant de commencer, assurez-vous d'avoir :
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Tesseract OCR (pour l'extraction de texte)

## Étape 1 : Installer les Dépendances

### 1.1 Installer Tesseract OCR

**Ubuntu/Debian :**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS :**
```bash
brew install tesseract
```

**Windows :**
Téléchargez et installez depuis : https://github.com/UB-Mannheim/tesseract/wiki

### 1.2 Installer les Dépendances Python

Ouvrez un terminal dans le dossier du projet et exécutez :

```bash
pip install -r requirements.txt
```

Cette commande installera toutes les bibliothèques nécessaires (YOLOv8, OpenCV, PyTorch, etc.)

### 1.3 Vérifier l'Installation

```bash
python check_dependencies.py
```

Ce script vérifie que toutes les dépendances sont correctement installées.

## Étape 2 : Préparer le Dataset (Optionnel - pour l'entraînement)

Si vous voulez entraîner votre propre modèle, vous avez besoin du dataset au format YOLO :

```
nuts_vision/
├── data.yaml
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

**Note :** Le dataset CompDetect peut être téléchargé depuis Roboflow (voir README.roboflow.txt)

## Étape 3 : Entraîner le Modèle (Si nécessaire)

Si vous n'avez pas encore de modèle entraîné :

```bash
# Entraînement rapide (modèle nano, 50 époques)
python src/train.py --data data.yaml --model-size n --epochs 50

# Entraînement complet (modèle moyen, 100 époques - recommandé)
python src/train.py --data data.yaml --model-size m --epochs 100
```

Le modèle sera sauvegardé dans : `runs/detect/component_detector/weights/best.pt`

**Durée :** L'entraînement peut prendre de 30 minutes à plusieurs heures selon votre matériel.

## Étape 4 : Tester avec une Photo

### Option A : Script de Test Simple (Recommandé pour débuter)

Utilisez le script de test simple qui détecte les composants sur une seule image :

```bash
python test_simple.py --model runs/detect/component_detector/weights/best.pt --image path/to/your/board_photo.jpg
```

Ce script va :
1. Détecter tous les composants
2. Afficher les résultats
3. Sauvegarder l'image annotée dans `outputs/results/`

### Option B : Pipeline Complet

Pour une analyse complète avec découpage et OCR :

```bash
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image path/to/your/board_photo.jpg
```

Le pipeline complet va :
1. Détecter les composants
2. Découper chaque composant individuellement
3. Extraire les numéros de pièce (MPN) des circuits intégrés
4. Générer des statistiques et visualisations

### Option C : Détection Uniquement (Sans OCR)

Si vous voulez juste détecter les composants sans OCR :

```bash
python src/detect.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image path/to/your/board_photo.jpg
```

## Étape 5 : Voir les Résultats

Les résultats sont sauvegardés dans le dossier `outputs/` :

```
outputs/
├── results/
│   ├── board_photo_detected.jpg    # Image avec annotations
│   ├── detections.json              # Détections au format JSON
│   └── mpn_results.csv              # Numéros de pièce extraits
├── cropped_components/              # Composants découpés
│   ├── board_photo_IC_0.jpg
│   ├── board_photo_resistor_0.jpg
│   └── ...
└── visualizations/                  # Graphiques statistiques
    ├── detection_statistics.png
    └── ocr_results.png
```

## Exemples d'Utilisation

### Exemple 1 : Test Rapide avec une Image

```bash
# Téléchargez une photo de carte électronique
# Placez-la dans le dossier du projet (par exemple: ma_carte.jpg)

# Détectez les composants
python src/detect.py --model runs/detect/component_detector/weights/best.pt --image ma_carte.jpg

# Ouvrez le résultat
# Le fichier sera dans: outputs/results/ma_carte_detected.jpg
```

### Exemple 2 : Analyser Plusieurs Images

```bash
# Placez vos images dans un dossier (par exemple: mes_cartes/)

# Analysez toutes les images
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image-dir mes_cartes/
```

### Exemple 3 : Extraction des Numéros de Pièce

```bash
# Pipeline complet avec OCR
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image ma_carte.jpg

# Les MPNs seront dans: outputs/results/mpn_results.csv
```

## Classes de Composants Détectés

Le système peut détecter 16 types de composants :

1. **IC** (Circuit Intégré)
2. **LED**
3. **Battery** (Batterie)
4. **Buzzer** (Buzzer/Sonnerie)
5. **Capacitor** (Condensateur)
6. **Clock** (Horloge)
7. **Connector** (Connecteur)
8. **Diode**
9. **Display** (Affichage)
10. **Fuse** (Fusible)
11. **Inductor** (Inductance)
12. **Potentiometer** (Potentiomètre)
13. **Relay** (Relais)
14. **Resistor** (Résistance)
15. **Switch** (Interrupteur)
16. **Transistor**

## Paramètres Importants

### Seuil de Confiance
Ajustez le seuil de confiance pour filtrer les détections :

```bash
# Plus strict (moins de faux positifs)
python src/detect.py --model best.pt --image photo.jpg --conf 0.5

# Plus permissif (plus de détections)
python src/detect.py --model best.pt --image photo.jpg --conf 0.2
```

### Désactiver l'OCR
Si vous ne voulez que la détection sans OCR :

```bash
python src/pipeline.py --model best.pt --image photo.jpg --no-ocr
```

### Désactiver les Visualisations
Pour accélérer le traitement :

```bash
python src/pipeline.py --model best.pt --image photo.jpg --no-viz
```

## Dépannage

### Erreur "No module named 'ultralytics'"
```bash
pip install -r requirements.txt
```

### Erreur "Tesseract not found"
Installez Tesseract OCR (voir Étape 1.1)

### Erreur "CUDA out of memory"
Utilisez un modèle plus petit :
```bash
python src/train.py --model-size n --batch 8
```

### Mauvais Résultats OCR
- Utilisez des images haute résolution
- Augmentez le padding : `--padding 20`
- Ajustez le seuil de confiance : `--conf 0.5`

## Aide Supplémentaire

Pour plus d'informations :
- **README.md** - Documentation complète en anglais
- **ARCHITECTURE.md** - Architecture du système
- **example.py** - Exemples de code Python

Pour afficher l'aide de chaque script :
```bash
python src/train.py --help
python src/detect.py --help
python src/pipeline.py --help
```

## Workflow Complet Recommandé

```bash
# 1. Vérifier les dépendances
python check_dependencies.py

# 2. Configurer le projet (optionnel)
python setup.py

# 3. Entraîner le modèle (si pas déjà fait)
python src/train.py --data data.yaml --epochs 100

# 4. Tester avec une photo
python test_simple.py --model runs/detect/component_detector/weights/best.pt --image ma_carte.jpg

# 5. Pipeline complet
python src/pipeline.py --model runs/detect/component_detector/weights/best.pt --image ma_carte.jpg

# 6. Voir les résultats
ls outputs/results/
cat outputs/results/mpn_results.csv
```

Bon travail ! 🚀
