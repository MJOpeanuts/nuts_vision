# Guide Rapide - Caméra Arducam 108MP

## Installation et Configuration

### 1. Prérequis Matériel
- Caméra Arducam 108MP avec focus motorisé (réf: B0494C)
- Port USB 3.0 disponible
- Câble USB 3.0 de qualité

### 2. Installation Logicielle

Toutes les dépendances sont déjà incluses dans `requirements.txt`. Installez-les avec:

```bash
pip install -r requirements.txt
```

## Utilisation de la Caméra

### Méthode 1: Interface Web (Recommandée)

1. **Démarrer l'interface web:**
   ```bash
   streamlit run app.py
   ```

2. **Naviguer vers "📷 Contrôle Caméra"** dans la barre latérale

3. **Connecter la caméra:**
   - Index de caméra: 0 (par défaut)
   - Résolution: 1920x1080 (recommandé)
   - Cliquer sur "🔌 Connect"

4. **Régler le focus:**
   - **Manuel:** Utiliser le curseur pour ajuster le focus (0-255)
   - **Automatique:** Cliquer sur "🔍 Auto Focus Scan"

5. **Capturer une photo:**
   - Ajuster la qualité JPEG (50-100)
   - Cliquer sur "📸 Capture Photo"

6. **Traiter la photo:**
   - Cliquer sur "🔄 Process Image"
   - Les résultats apparaîtront dans le "Job Viewer"

### Méthode 2: Script Python

**Exemple basique:**

```python
from src.camera_control import ArducamCamera

# Connexion
camera = ArducamCamera(camera_index=0)
camera.connect(width=1920, height=1080)

# Auto-focus
camera.auto_focus_scan()

# Capture
photo = camera.capture_photo()
print(f"Photo sauvegardée: {photo}")

# Déconnexion
camera.disconnect()
```

**Exemple avec pipeline complet:**

```python
from src.camera_control import ArducamCamera
from src.pipeline import ComponentAnalysisPipeline

# Initialiser caméra et pipeline
camera = ArducamCamera(camera_index=0)
pipeline = ComponentAnalysisPipeline(
    model_path="runs/detect/component_detector/weights/best.pt",
    use_database=True
)

# Connecter et capturer
camera.connect(width=1920, height=1080)
camera.auto_focus_scan()
photo = camera.capture_photo()

# Analyser
results = pipeline.process_image(photo)
print(f"Composants détectés: {len(results['detections'])}")

camera.disconnect()
```

### Méthode 3: Scripts d'Exemple

**Test basique de la caméra:**
```bash
python example_camera.py
```

**Capture et analyse complète:**
```bash
python example_camera_pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --num-photos 3 \
  --use-database
```

## Workflow Recommandé

### Pour Analyser une Carte Électronique:

1. **Préparation:**
   - Placer la carte à 10-30 cm de la caméra
   - Assurer un éclairage uniforme et suffisant
   - Stabiliser la caméra (trépied recommandé)

2. **Connexion:**
   ```python
   camera = ArducamCamera(camera_index=0)
   camera.connect(width=1920, height=1080)
   ```

3. **Mise au point:**
   ```python
   # Automatique (recommandé)
   best_focus, sharpness = camera.auto_focus_scan()
   
   # Ou manuel
   camera.set_focus(150)  # Ajuster selon la distance
   ```

4. **Capture:**
   ```python
   photo_path = camera.capture_photo(quality=95)
   ```

5. **Traitement:**
   ```python
   pipeline = ComponentAnalysisPipeline(model_path="path/to/model.pt")
   results = pipeline.process_image(photo_path)
   ```

6. **Résultats:**
   - Composants détectés: `results['detections']`
   - Numéros de pièce: `results['ocr_results']`

## Paramètres Optimaux

### Résolutions Recommandées:

**Pour la prévisualisation:**
- 1280x720 @ 30fps - Rapide, bon pour ajuster le focus

**Pour la capture finale:**
- 1920x1080 @ 15fps - Bon équilibre qualité/vitesse
- 2560x1440 @ 10fps - Haute qualité pour petits composants
- 3840x2160 @ 10fps - Très haute qualité (si supporté)

### Qualité JPEG:
- **85-90**: Bon équilibre taille/qualité
- **95**: Haute qualité (recommandé pour OCR)
- **100**: Qualité maximale (fichiers volumineux)

### Focus:
- **0-50**: Objets très proches (< 10 cm)
- **50-150**: Distance normale (10-30 cm) - **Recommandé**
- **150-255**: Objets éloignés (> 30 cm)

## Dépannage

### Caméra Non Détectée

**Symptôme:** "Could not open camera at index 0"

**Solutions:**
1. Vérifier que la caméra est branchée sur un port USB 3.0
2. Vérifier que le voyant LED de la caméra est allumé
3. Essayer différents index (0, 1, 2...)
4. Linux: Ajouter l'utilisateur au groupe `video`
   ```bash
   sudo usermod -a -G video $USER
   ```
5. Vérifier les permissions:
   ```bash
   ls -l /dev/video*
   ```

### Focus Ne Fonctionne Pas

**Solutions:**
1. Attendre 0.5-1 seconde après chaque ajustement
2. Essayer des pas plus grands (ex: 0 → 100 → 200)
3. Utiliser l'auto-focus au lieu du manuel
4. Vérifier que l'autofocus est désactivé

### Images Floues

**Solutions:**
1. Utiliser l'auto-focus scan
2. Vérifier l'éclairage (doit être uniforme et suffisant)
3. Stabiliser la caméra (utiliser un trépied)
4. Nettoyer l'objectif
5. Augmenter la résolution de capture

### Mauvaise Qualité OCR

**Solutions:**
1. Utiliser une résolution plus élevée (1920x1080 minimum)
2. Améliorer l'éclairage
3. Utiliser la qualité JPEG maximale (95-100)
4. S'assurer que le focus est optimal
5. Positionner la caméra perpendiculairement à la carte

## Conseils de Performance

### Pour de Meilleurs Résultats:

1. **Éclairage:**
   - Utiliser un éclairage diffus et uniforme
   - Éviter les ombres et les reflets
   - Lumière LED blanche recommandée

2. **Distance:**
   - 10-30 cm optimal pour la plupart des cartes
   - Ajuster selon la taille des composants

3. **Focus:**
   - Lancer l'auto-focus une fois au début
   - Pas besoin de le relancer pour chaque photo (si distance constante)

4. **Qualité:**
   - Utiliser 95 de qualité JPEG pour l'OCR
   - Peut réduire à 85 pour le stockage

5. **Workflow:**
   - Capturer d'abord, traiter ensuite (batch)
   - Permet de vérifier visuellement avant traitement

## API Complète

### Classe ArducamCamera

**Méthodes principales:**

```python
# Connexion
camera.connect(width=1920, height=1080, fps=30) -> bool

# Déconnexion
camera.disconnect()

# Focus manuel
camera.set_focus(focus_value: int) -> bool  # 0-255

# Lire le focus actuel
camera.get_focus() -> int

# Auto-focus
camera.auto_focus_scan(start=0, end=255, step=10) -> (int, float)

# Capturer une frame
camera.capture_frame() -> np.ndarray

# Capturer et sauvegarder
camera.capture_photo(output_path=None, quality=95) -> str

# Informations caméra
camera.get_camera_info() -> dict
```

## Ressources

### Documentation:
- **Guide complet:** [CAMERA.md](CAMERA.md)
- **README:** [README_FR.md](README_FR.md)

### Support:
- **Caméra Arducam:** https://www.arducam.com/support/
- **nuts_vision:** https://github.com/MJOpeanuts/nuts_vision/issues

### Produit:
- **Arducam 108MP:** https://www.arducam.com/arducam-108mp-motorized-focus-usb-3-0-camera-module.html

## Questions Fréquentes

**Q: Puis-je utiliser plusieurs caméras simultanément?**
A: Oui, créez plusieurs instances avec des index différents:
```python
camera1 = ArducamCamera(camera_index=0)
camera2 = ArducamCamera(camera_index=1)
```

**Q: Comment choisir la meilleure résolution?**
A: Dépend de votre cas:
- Prévisualisation: 1280x720
- Analyse standard: 1920x1080
- Petits composants: 2560x1440 ou plus

**Q: L'auto-focus est-il nécessaire?**
A: Fortement recommandé pour des résultats optimaux. Il trouve automatiquement le meilleur focus.

**Q: Combien de temps prend l'auto-focus?**
A: Environ 15-30 secondes selon les paramètres (start, end, step).

**Q: Puis-je sauvegarder les photos en PNG?**
A: Actuellement seul JPEG est supporté. Vous pouvez convertir après avec PIL/Pillow si nécessaire.
