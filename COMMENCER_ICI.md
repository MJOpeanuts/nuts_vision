# 🚀 COMMENCER ICI / START HERE

## Pour les utilisateurs francophones 🇫🇷

Bienvenue dans **nuts_vision** ! Voici comment démarrer en 5 minutes.

### Étape 1 : Installation (5 minutes)

```bash
# 1. Installer Tesseract OCR
# Ubuntu/Debian:
sudo apt-get update && sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows: téléchargez depuis https://github.com/UB-Mannheim/tesseract/wiki

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Vérifier l'installation
python check_dependencies.py
```

### Étape 2 : Entraîner le Modèle (30 min - 2h selon votre ordinateur)

**Important :** Vous devez d'abord avoir le dataset. Téléchargez-le depuis Roboflow (voir README.roboflow.txt) et extrayez-le dans le dossier du projet.

```bash
# Entraînement rapide (pour tester)
python src/train.py --data data.yaml --model-size n --epochs 50

# OU entraînement complet (recommandé pour de meilleurs résultats)
python src/train.py --data data.yaml --model-size m --epochs 100
```

Le modèle sera sauvegardé dans : `runs/detect/component_detector/weights/best.pt`

### Étape 3 : Tester avec une Photo (30 secondes)

```bash
# Remplacez "ma_carte.jpg" par le chemin vers votre photo
python test_simple.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image ma_carte.jpg
```

Le résultat sera dans : `outputs/results/ma_carte_detected.jpg`

### C'est tout ! 🎉

**Pour aller plus loin :**
- 📖 [Guide détaillé en français](DEMARRAGE_RAPIDE.md)
- 📚 [Documentation complète en français](README_FR.md)

---

## For English speakers 🇬🇧

Welcome to **nuts_vision**! Here's how to get started in 5 minutes.

### Step 1: Installation (5 minutes)

```bash
# 1. Install Tesseract OCR
# Ubuntu/Debian:
sudo apt-get update && sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows: download from https://github.com/UB-Mannheim/tesseract/wiki

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Verify installation
python check_dependencies.py
```

### Step 2: Train the Model (30 min - 2h depending on your hardware)

**Important:** You need the dataset first. Download it from Roboflow (see README.roboflow.txt) and extract it to the project folder.

```bash
# Quick training (for testing)
python src/train.py --data data.yaml --model-size n --epochs 50

# OR full training (recommended for best results)
python src/train.py --data data.yaml --model-size m --epochs 100
```

The model will be saved to: `runs/detect/component_detector/weights/best.pt`

### Step 3: Test with a Photo (30 seconds)

```bash
# Replace "my_board.jpg" with your image path
python test_simple.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image my_board.jpg
```

The result will be in: `outputs/results/my_board_detected.jpg`

### That's it! 🎉

**To go further:**
- 📖 [Quick start guide](QUICKSTART.md)
- 📚 [Complete documentation](README.md)

---

## 💡 Astuces / Tips

### Si vous n'avez pas le dataset / If you don't have the dataset

Vous devez télécharger le dataset CompDetect depuis Roboflow. Voir les détails dans `README.roboflow.txt`.

You need to download the CompDetect dataset from Roboflow. See details in `README.roboflow.txt`.

### Si le modèle prend trop de temps / If training takes too long

Utilisez un modèle plus petit et moins d'époques:

Use a smaller model and fewer epochs:

```bash
python src/train.py --data data.yaml --model-size n --epochs 25 --batch 8
```

### Pour tester sans entraîner / To test without training

Si quelqu'un partage un modèle pré-entraîné (.pt file), vous pouvez l'utiliser directement:

If someone shares a pre-trained model (.pt file), you can use it directly:

```bash
python test_simple.py --model chemin/vers/modele.pt --image ma_photo.jpg
```

---

## 🆘 Besoin d'aide ? / Need help?

- **Français :** Consultez [DEMARRAGE_RAPIDE.md](DEMARRAGE_RAPIDE.md)
- **English:** Check [QUICKSTART.md](QUICKSTART.md)
- **Issues:** Ouvrez une issue sur GitHub / Open an issue on GitHub

Bon courage ! 🚀
