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
   - Choisir une résolution prédéfinie ou personnalisée:
     - HD 720p@60fps - **Fluide et rapide (Recommandé pour prévisualisation)**
     - 4K UHD@10fps - Haute qualité
     - 4000x3000@7fps - Ultra haute qualité
     - HD 720p@30fps - Prévisualisation
     - VGA@30fps - Basse qualité
     - Personnalisée - Définir vos propres valeurs
   - Cliquer sur "🔌 Connect"
   - Les informations de la caméra s'afficheront (résolution, FPS, focus actuel)

4. **Activer la prévisualisation en direct:**
   - Cliquer sur "▶️ Start Live Preview" pour voir le flux vidéo en temps réel
   - L'image se rafraîchit automatiquement pour faciliter le réglage du focus
   - Le score de netteté (sharpness) s'affiche pour vous aider à optimiser le focus
   - Cliquer sur "⏸️ Stop Live Preview" pour arrêter

5. **Régler le focus:**
   - **Manuel:** 
     - Activer la prévisualisation en direct (recommandé)
     - Utiliser le curseur pour ajuster le focus (0-1023)
     - Le changement s'applique instantanément
     - Observer la netteté dans la prévisualisation
   - **Automatique:** Cliquer sur "🔍 Auto Focus Scan"
   - **Presets rapides:**
     - "📍 Near" pour objets proches (~10cm) - valeur 200
     - "📍 Mid" pour distance moyenne (~20cm) - valeur 500
     - "📍 Far" pour objets éloignés (~30cm+) - valeur 800

6. **Capturer une photo:**
   - Ajuster la qualité JPEG (50-100, recommandé: 95)
   - Cliquer sur "📸 Capture Photo"
   - La photo capturée s'affiche automatiquement

7. **Traiter la photo:**
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
   # Pour prévisualisation et réglage: HD 720p à 60fps
   camera.connect(width=1280, height=720, fps=60)
   ```

3. **Mise au point avec prévisualisation en direct (interface web):**
   - Activer "▶️ Start Live Preview"
   - Ajuster le curseur de focus (0-1023) tout en observant l'image
   - Observer le score de netteté (sharpness) - plus élevé = plus net
   - Ou utiliser "🔍 Auto Focus Scan" pour trouver automatiquement le meilleur focus

4. **Mise au point (script Python):**
   ```python
   # Automatique (recommandé) - utilise la nouvelle plage 0-1023
   best_focus, sharpness = camera.auto_focus_scan(start=0, end=1023, step=50)
   
   # Ou manuel - valeurs typiques pour PCB
   camera.set_focus(500)  # Distance moyenne ~20cm
   ```

5. **Reconnexion en haute résolution (optionnel):**
   ```python
   camera.disconnect()
   # 4K UHD pour capture haute qualité
   camera.connect(width=3840, height=2160, fps=10)
   camera.set_focus(best_focus)  # Réappliquer le focus optimal
   ```

6. **Capture:**
   ```python
   photo_path = camera.capture_photo(quality=95)
   ```

7. **Traitement:**
   ```python
   pipeline = ComponentAnalysisPipeline(model_path="path/to/model.pt")
   results = pipeline.process_image(photo_path)
   ```

8. **Résultats:**
   - Composants détectés: `results['detections']`
   - Numéros de pièce: `results['ocr_results']`

## Paramètres Optimaux

### Résolutions Recommandées (Arducam 108MP):

**Pour la prévisualisation en direct:**
- 1280x720 @ 60fps - **Idéal pour ajuster le focus** (très rapide et fluide) ⭐
- 1280x720 @ 30fps - Prévisualisation standard

**Pour la capture finale:**
- 1280x720 @ 60fps - **Recommandé pour usage général** - Rapide et fluide
- 3840x2160 @ 10fps - 4K UHD - Haute qualité pour petits composants
- 4000x3000 @ 7fps - Ultra haute qualité - Résolution maximale pratique
- 12000x9000 @ 1fps - 108MP - Nécessite l'application demo Arducam

💡 **Note importante:** La résolution 108MP (12000x9000) n'est accessible que via l'application demo Arducam. Pour une utilisation quotidienne, privilégiez les résolutions jusqu'à 4000x3000.

### Qualité JPEG:
- **85-90**: Bon équilibre taille/qualité
- **95**: Haute qualité - **Recommandé pour OCR**
- **100**: Qualité maximale (fichiers volumineux)

### Focus (Arducam 108MP - Plage 0-1023):
- **0-200**: Objets très proches (< 10 cm)
- **200-600**: Distance normale (10-30 cm) - **Recommandé pour PCB**
- **600-1023**: Objets éloignés (> 30 cm)

💡 **Astuce:** Utilisez la prévisualisation en direct avec le score de netteté (sharpness) pour trouver le focus optimal. Plus le score est élevé, plus l'image est nette!

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
- Prévisualisation et réglage du focus: **1280x720@60fps** - Très rapide et fluide ⭐
- Analyse standard: 1280x720@60fps ou 3840x2160@10fps
- Petits composants: 4000x3000@7fps - Résolution maximale pratique
- 108MP (12000x9000): Nécessite l'application demo Arducam

**Q: Quelle est la plage de focus de la caméra Arducam 108MP?**
A: La plage de focus est de **0 à 1023** (et non 0-255). Valeurs typiques:
- 0-200: Très proche (< 10cm)
- 200-600: Distance moyenne (10-30cm) - **Recommandé pour PCB**
- 600-1023: Éloigné (> 30cm)

**Q: La prévisualisation en direct est-elle nécessaire?**
A: Non, mais elle est **fortement recommandée** pour le réglage du focus. Elle vous permet de:
- Voir les changements de focus en temps réel
- Visualiser le score de netteté (sharpness) pour optimiser le focus
- Ajuster la position de la caméra et l'éclairage avant la capture

**Q: La prévisualisation ralentit mon ordinateur, que faire?**
A: Utilisez une résolution plus basse (640x480 ou 1280x720) pour la prévisualisation. Vous pourrez toujours vous reconnecter en haute résolution pour la capture finale.

**Q: L'auto-focus est-il nécessaire?**
A: Fortement recommandé pour des résultats optimaux. Il trouve automatiquement le meilleur focus.

**Q: Combien de temps prend l'auto-focus?**
A: Environ 15-30 secondes selon les paramètres (start, end, step).

**Q: Puis-je sauvegarder les photos en PNG?**
A: Actuellement seul JPEG est supporté. Vous pouvez convertir après avec PIL/Pillow si nécessaire.

**Q: Quelle est la différence entre "Capture Single Frame" et "Capture Photo"?**
A: 
- **Capture Single Frame**: Affiche une image à l'écran pour vérification, ne sauvegarde pas
- **Capture Photo**: Sauvegarde l'image sur le disque avec la qualité JPEG spécifiée

**Q: Comment savoir si mon focus est optimal?**
A: 
1. Utilisez la prévisualisation en direct
2. Regardez le score de netteté (sharpness) - plus il est élevé, mieux c'est
3. Pour les PCB, un score > 100 est généralement bon, > 200 est excellent
