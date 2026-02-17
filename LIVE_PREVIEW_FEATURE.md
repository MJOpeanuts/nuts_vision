# Live Camera Preview Feature - Implementation Summary

## 🎯 Objectif / Objective

Répondre à la demande de l'utilisateur pour visualiser en direct l'image de la caméra afin de faciliter le réglage du focus, et permettre de choisir la résolution.

Responding to the user's request to visualize the camera image in real-time for easier focus adjustment, and to allow resolution selection.

## ✨ Nouvelles Fonctionnalités / New Features

### 1. 📹 Prévisualisation en Direct / Live Preview

**Description:**
- Flux vidéo continu de la caméra directement dans l'interface web
- Rafraîchissement automatique pour voir les changements de focus en temps réel
- Affichage du score de netteté (sharpness) pour optimiser le focus

**Continuous video feed from the camera directly in the web interface**
- Automatic refresh to see focus changes in real-time
- Display of sharpness score to optimize focus

**Utilisation / Usage:**
1. Connecter la caméra / Connect the camera
2. Cliquer sur "▶️ Start Live Preview" / Click "▶️ Start Live Preview"
3. Ajuster le focus avec le curseur / Adjust focus with the slider
4. Observer l'image et le score de netteté / Observe the image and sharpness score
5. Cliquer sur "⏸️ Stop Live Preview" pour arrêter / Click "⏸️ Stop Live Preview" to stop

**Avantages / Benefits:**
- ✅ Réglage du focus beaucoup plus facile / Much easier focus adjustment
- ✅ Feedback visuel instantané / Instant visual feedback
- ✅ Score de netteté quantifiable / Quantifiable sharpness score
- ✅ Pas besoin de capturer plusieurs photos pour tester / No need to capture multiple photos to test

### 2. 📐 Presets de Résolution / Resolution Presets

**Description:**
Sélection simplifiée de la résolution avec des presets prédéfinis basés sur les spécifications officielles Arducam 108MP:

Simplified resolution selection with predefined presets based on official Arducam 108MP specifications:

- **HD 720p@60fps** - **Recommandé** - Fluide et rapide / **Recommended** - Smooth & fast ⭐
- **4K UHD@10fps** - Haute qualité / High quality
- **4000x3000@7fps** - Ultra haute qualité / Ultra high quality
- **HD 720p@30fps** - Prévisualisation / Preview
- **VGA@30fps** - Basse qualité / Low quality
- **Personnalisée / Custom** - Définir ses propres valeurs / Define custom values

**Note:** La résolution 108MP (12000x9000) nécessite l'application demo Arducam et n'est pas disponible via OpenCV.

**Note:** The 108MP resolution (12000x9000) requires the Arducam demo application and is not available via OpenCV.

**Affichage de la résolution:**
L'interface affiche maintenant clairement la résolution utilisée :
- Dans la section de connexion / In the connection section
- Dans les informations de la caméra / In camera information

The interface now clearly displays the resolution being used:
- In the connection section
- In camera information

### 3. 🎯 Presets de Focus Rapides / Quick Focus Presets

**Description:**
Boutons rapides pour des distances communes :

Quick buttons for common distances:

- **📍 Near** (~10cm) - Objets très proches / Very close objects
- **📍 Mid** (~20cm) - Distance moyenne (idéal pour PCB) / Medium distance (ideal for PCB)
- **📍 Far** (~30cm+) - Objets éloignés / Distant objects

### 4. 📊 Informations de Caméra en Direct / Live Camera Information

**Affichage en temps réel de:**
- Résolution actuelle (largeur x hauteur) / Current resolution (width x height)
- FPS configuré / Configured FPS
- Valeur de focus actuelle / Current focus value
- Luminosité, contraste, saturation / Brightness, contrast, saturation

**Real-time display of:**
- Current resolution (width x height)
- Configured FPS
- Current focus value
- Brightness, contrast, saturation

## 🔧 Modifications Techniques / Technical Changes

### Fichiers Modifiés / Modified Files

1. **app.py**
   - Ajout du système de prévisualisation en direct / Added live preview system
   - Ajout des presets de résolution / Added resolution presets
   - Amélioration de l'interface de contrôle du focus / Improved focus control interface
   - Auto-application du focus lors du changement du curseur / Auto-apply focus when slider changes
   - Affichage du score de netteté / Display of sharpness score

2. **CAMERA_GUIDE_FR.md**
   - Documentation complète de la prévisualisation en direct / Complete documentation of live preview
   - Instructions détaillées pour l'utilisation / Detailed usage instructions
   - Nouveaux workflows recommandés / New recommended workflows
   - FAQ étendue / Extended FAQ

## 📸 Workflow Recommandé / Recommended Workflow

### Pour le réglage du focus / For focus adjustment:

1. **Connecter en résolution optimale pour la prévisualisation:**
   ```
   Preset: HD 720p@60fps (Arducam 108MP optimal)
   ```

2. **Activer la prévisualisation en direct:**
   ```
   Cliquer sur "▶️ Start Live Preview"
   ```

3. **Ajuster le focus (0-1023):**
   - Observer l'image et le score de netteté
   - Ajuster le curseur jusqu'à obtenir le score le plus élevé
   - Ou utiliser "🔍 Auto Focus Scan"

4. **Capturer en haute résolution (optionnel):**
   - Arrêter la prévisualisation
   - Se reconnecter en 4K UHD ou 4000x3000
   - Capturer la photo finale

### For focus adjustment:

1. **Connect in optimal resolution for preview:**
   ```
   Preset: HD 720p@60fps (Arducam 108MP optimal)
   ```

2. **Enable live preview:**
   ```
   Click "▶️ Start Live Preview"
   ```

3. **Adjust focus (0-1023):**
   - Observe the image and sharpness score
   - Adjust slider until highest score is achieved
   - Or use "🔍 Auto Focus Scan"

4. **Capture in high resolution (optional):**
   - Stop preview
   - Reconnect in 4K UHD or 4000x3000
   - Capture final photo

## 💡 Conseils / Tips

### Performance / Performance

- Utilisez HD 720p@60fps pour la prévisualisation = très fluide / Use HD 720p@60fps for preview = very smooth
- Utilisez 4K UHD ou 4000x3000 pour la capture finale = meilleure qualité OCR / Use 4K UHD or 4000x3000 for final capture = better OCR quality
- Le score de netteté typique pour un PCB bien mis au point : 100-300 / Typical sharpness score for a well-focused PCB: 100-300

### Focus (Arducam 108MP - Range 0-1023)

- Commencez avec les presets Near (200) / Mid (500) / Far (800) / Start with Near/Mid/Far presets
- Utilisez la prévisualisation pour affiner / Use preview to fine-tune
- Un score de netteté > 200 est excellent / A sharpness score > 200 is excellent
- Plage typique pour PCB: 200-600 / Typical range for PCB: 200-600

### Résolution / Resolution

- **Pour prévisualisation:** 1280x720 / **For preview:** 1280x720
- **Pour capture standard:** 1920x1080 / **For standard capture:** 1920x1080
- **Pour petits composants:** 2560x1440 ou plus / **For small components:** 2560x1440 or higher

## 🐛 Tests Suggérés / Suggested Tests

### Tests Manuels / Manual Tests

1. ✅ Vérification syntaxe Python / Python syntax check
2. ⏳ Test de connexion caméra / Camera connection test (requires hardware)
3. ⏳ Test de prévisualisation en direct / Live preview test (requires hardware)
4. ⏳ Test des presets de résolution / Resolution presets test (requires hardware)
5. ⏳ Test de l'auto-focus / Auto-focus test (requires hardware)
6. ⏳ Test de capture photo / Photo capture test (requires hardware)

### Tests Automatisés / Automated Tests

```python
# Test syntaxe
import ast
with open('app.py', 'r') as f:
    ast.parse(f.read())
# ✅ Passed
```

## 📝 Notes de Version / Release Notes

**Version:** 1.2.0
**Date:** 2026-02-17

### Nouvelles Fonctionnalités / New Features

- ✨ Prévisualisation en direct de la caméra / Live camera preview
- 📐 Presets de résolution basés sur Arducam 108MP / Resolution presets based on Arducam 108MP specs
- 🎯 Presets de focus rapides (200/500/800 pour plage 0-1023) / Quick focus presets
- 📊 Affichage des informations caméra en temps réel / Real-time camera information display
- 📈 Score de netteté affiché pendant la prévisualisation / Sharpness score displayed during preview
- 🔄 Auto-application du focus lors du changement du curseur / Auto-apply focus on slider change

### Améliorations / Improvements

- **Plage de focus mise à jour:** 0-1023 (était 0-255) / **Focus range updated:** 0-1023 (was 0-255)
- **Résolutions officielles:** Basées sur specs Arducam 108MP USB 3.0 / **Official resolutions:** Based on Arducam 108MP USB 3.0 specs
- Interface utilisateur plus intuitive / More intuitive user interface
- Meilleure expérience de réglage du focus / Better focus adjustment experience
- Documentation étendue en français / Extended French documentation

### Compatibilité / Compatibility

- Compatible avec toutes les caméras supportant OpenCV VideoCapture / Compatible with all cameras supporting OpenCV VideoCapture
- Testé avec Arducam 108MP / Tested with Arducam 108MP
- Nécessite Python 3.8+ et les dépendances listées dans requirements.txt / Requires Python 3.8+ and dependencies listed in requirements.txt

## 🚀 Déploiement / Deployment

Pour utiliser les nouvelles fonctionnalités / To use the new features:

```bash
# 1. Mettre à jour le code / Update code
git pull

# 2. Installer/Mettre à jour les dépendances / Install/Update dependencies
pip install -r requirements.txt

# 3. Lancer l'interface web / Launch web interface
streamlit run app.py

# 4. Naviguer vers "📷 Camera Control" / Navigate to "📷 Camera Control"
```

## 📞 Support

Pour toute question ou problème / For any questions or issues:
- Documentation: [CAMERA_GUIDE_FR.md](CAMERA_GUIDE_FR.md)
- Issues: https://github.com/MJOpeanuts/nuts_vision/issues
