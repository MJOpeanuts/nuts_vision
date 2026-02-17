# Configuration Arducam 108MP - Spécifications Officielles

## 📷 À propos de la Caméra

**Modèle:** Arducam 108MP Ultra-high Resolution Motorized Focus USB 3.0 Camera

### Caractéristiques Principales

- **Capteur:** 1/1.52" CMOS
- **Résolution Maximale:** 12000x9000 pixels (108 mégapixels)
- **Champ de Vision:** 85°(D)
- **Interface:** USB 3.0
- **Objectif:** Focus motorisé haute qualité
- **Format de Sortie:** YUYV (images non compressées de haute qualité)

## 📐 Résolutions et Fréquences d'Images Supportées

### Via USB 3.0 (OpenCV/V4L2)

| Résolution | FPS | Usage Recommandé |
|-----------|-----|------------------|
| **1280x720** | **60** | ⭐ **Prévisualisation fluide, réglage du focus** |
| 1280x720 | 30 | Prévisualisation standard |
| **3840x2160** | **10** | 4K UHD - Haute qualité |
| **4000x3000** | **7** | Ultra haute qualité - Maximum pratique |
| 12000x9000 | 1 | 108MP - **Nécessite l'application demo** ⚠️ |

### Notes Importantes

1. **Résolution 108MP (12000x9000):** 
   - Cette résolution n'est accessible que via l'application demo fournie par Arducam
   - Non disponible directement via OpenCV/V4L2
   - Pour usage quotidien, privilégiez les résolutions jusqu'à 4000x3000@7fps

2. **Résolutions Recommandées pour nuts_vision:**
   - **Prévisualisation/Focus:** 1280x720@60fps (fluide, temps réel)
   - **Capture Standard:** 1280x720@60fps ou 3840x2160@10fps
   - **Haute Qualité:** 4000x3000@7fps

## 🎯 Configuration du Focus

### Plage de Focus: 0-1023

La caméra Arducam 108MP utilise une **plage de focus de 0 à 1023** (et non 0-255 comme certaines caméras).

### Valeurs Typiques

| Valeur | Distance Approximative | Usage |
|--------|----------------------|-------|
| 0-200 | < 10 cm | Macro, objets très proches |
| **200-600** | **10-30 cm** | **PCB et composants électroniques** ⭐ |
| 600-1023 | > 30 cm | Objets éloignés |

### Presets Recommandés

- **Near (Proche):** 200 - Pour objets à ~10cm
- **Mid (Moyen):** 500 - Pour PCB à ~20cm ⭐ **Recommandé**
- **Far (Éloigné):** 800 - Pour objets à ~30cm+

### Réglage du Focus

#### Réglage Manuel

```python
from src.camera_control import ArducamCamera

camera = ArducamCamera(camera_index=0)
camera.connect(width=1280, height=720, fps=60)

# Définir une valeur spécifique (0-1023)
camera.set_focus(500)  # Distance moyenne, idéal pour PCB
```

#### Réglage Automatique (Auto-focus)

```python
# Auto-focus avec balayage de la plage complète
best_focus, sharpness = camera.auto_focus_scan(
    start=0,      # Début de la plage
    end=1023,     # Fin de la plage
    step=50       # Pas de balayage
)

print(f"Focus optimal trouvé: {best_focus}")
print(f"Score de netteté: {sharpness:.2f}")
```

#### Calibration pour Application Spécifique

Pour la photographie de composants électroniques:

1. **Positionner** la caméra à une distance fixe (ex: 20cm)
2. **Activer** la prévisualisation en direct
3. **Ajuster** le curseur de focus (0-1023)
4. **Observer** le score de netteté (viser > 200)
5. **Noter** la valeur optimale pour usage futur

```python
# Exemple de valeur calibrée pour PCB à 20cm
CALIBRATED_FOCUS_PCB = 500
camera.set_focus(CALIBRATED_FOCUS_PCB)
```

## ⚙️ Configuration dans nuts_vision

### Interface Web (app.py)

Les presets de résolution ont été configurés selon les spécifications:

```python
resolution_presets = {
    "HD 720p@60fps - Fast & Smooth": (1280, 720, 60),      # ⭐ Recommandé
    "4K UHD@10fps - High Quality": (3840, 2160, 10),
    "4000x3000@7fps - Ultra High Quality": (4000, 3000, 7),
    "HD 720p@30fps - Preview": (1280, 720, 30),
    "VGA@30fps - Low Quality": (640, 480, 30),
    "Custom": None
}
```

### Curseur de Focus

- **Plage:** 0-1023
- **Pas:** 1
- **Défaut:** Valeur actuelle de la caméra

### Auto-focus

- **Plage de balayage:** 0-1023
- **Pas:** 50 (ajustable)
- **Durée:** ~30-45 secondes (dépend du pas)

## 🔧 Workflow Recommandé

### Pour Analyse de PCB

1. **Connexion:**
   ```
   Résolution: HD 720p@60fps
   Index: 0 (par défaut)
   ```

2. **Réglage du Focus:**
   - Activer la prévisualisation en direct
   - Utiliser le curseur (0-1023) ou auto-focus
   - Viser un score de netteté > 200

3. **Capture (optionnel - haute résolution):**
   - Déconnecter
   - Reconnecter en 4K ou 4000x3000
   - Réappliquer la valeur de focus trouvée
   - Capturer

4. **Traitement:**
   - Utiliser le pipeline de détection
   - OCR sur les composants IC

## 📊 Performances

### Temps de Capture (approximatifs)

| Résolution | FPS | Temps par Frame |
|-----------|-----|-----------------|
| 1280x720 | 60 | ~17ms (très rapide) |
| 3840x2160 | 10 | ~100ms |
| 4000x3000 | 7 | ~143ms |

### Temps d'Auto-focus

- **Plage complète (0-1023, step=50):** ~30-45 secondes
- **Plage réduite (200-600, step=25):** ~15-20 secondes
- **Plage très réduite (400-600, step=10):** ~5-10 secondes

## 🎯 Optimisations

### Pour Prévisualisation en Direct

```python
# Configuration optimale pour prévisualisation fluide
camera.connect(width=1280, height=720, fps=60)
```

**Avantages:**
- 60 FPS = prévisualisation très fluide
- Faible latence pour réglage du focus
- Bonne qualité pour visualisation

### Pour Capture de Qualité

```python
# Configuration pour capture haute qualité
camera.connect(width=4000, height=3000, fps=7)
```

**Avantages:**
- Résolution maximale pratique (sans demo app)
- Excellente pour OCR de petits composants
- Bon compromis qualité/vitesse

### Auto-focus Optimisé pour PCB

```python
# Balayage ciblé pour PCB (distance typique 15-25cm)
best_focus, sharpness = camera.auto_focus_scan(
    start=300,    # Plus proche que nécessaire
    end=700,      # Plus loin que nécessaire
    step=25       # Bon équilibre vitesse/précision
)
```

## 🐛 Dépannage

### Focus ne Change Pas

**Symptômes:**
- Le curseur bouge mais l'image ne change pas
- Valeurs 0-255 utilisées au lieu de 0-1023

**Solutions:**
1. Vérifier que vous utilisez la plage 0-1023
2. Essayer des changements plus importants (par exemple: 0 → 500 → 1023)
3. Attendre 0.5-1 seconde après chaque ajustement
4. Vérifier que l'autofocus de la caméra est désactivé

### Résolution Non Supportée

**Symptômes:**
- Erreur lors de la connexion
- Image floue ou déformée

**Solutions:**
1. Utiliser uniquement les résolutions listées dans ce document
2. Pour 108MP, utiliser l'application demo Arducam
3. Vérifier le câble USB 3.0

### Prévisualisation Saccadée

**Symptômes:**
- Prévisualisation lente ou saccadée
- Taux de rafraîchissement faible

**Solutions:**
1. Réduire la résolution à 1280x720
2. Augmenter le FPS à 60
3. Réduire le taux de rafraîchissement dans l'interface web

## 📝 Références

### Documentation Officielle
- Arducam 108MP Product Page
- USB 3.0 Camera User Guide

### Outils Utiles (Linux)

```bash
# Lister les caméras disponibles
v4l2-ctl --list-devices

# Voir les formats supportés
v4l2-ctl --list-formats-ext

# Régler le focus manuellement
v4l2-ctl --set-ctrl=focus_absolute=500

# Désactiver l'autofocus
v4l2-ctl --set-ctrl=focus_auto=0
```

## 📌 Résumé des Changements

### Anciennes Valeurs (Incorrectes)
- Focus: 0-255
- Résolutions: 1920x1080@30fps, 2560x1440@15fps, etc.
- Presets focus: 50, 125, 200

### Nouvelles Valeurs (Correctes - Arducam 108MP)
- Focus: **0-1023** ✅
- Résolutions: **720p@60fps, 4K@10fps, 4000x3000@7fps** ✅
- Presets focus: **200, 500, 800** ✅

---

**Version:** 1.2.0  
**Date:** 2026-02-17  
**Caméra:** Arducam 108MP USB 3.0 (B0494C)
