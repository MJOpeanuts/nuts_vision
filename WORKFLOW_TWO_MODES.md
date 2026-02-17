# Guide du Workflow Simplifié - Système à Deux Modes

## 🎯 Vue d'Ensemble

Le système de caméra Arducam a été simplifié en **deux modes distincts** pour un workflow optimal:

### 🎥 Mode Preview (Prévisualisation)
**Objectif:** Réglages rapides et fluides
- Résolution fixe: **1280x720 @ 60fps**
- Prévisualisation en direct très fluide (10 FPS)
- Tous les contrôles disponibles: focus, exposition, luminosité, contraste, etc.
- Parfait pour ajuster tous les paramètres

### 📸 Mode Scan (Capture)
**Objectif:** Captures haute qualité
- Choix de résolution:
  - **4K UHD:** 3840x2160 @ 10fps
  - **Ultra High Quality:** 4000x3000 @ 7fps
- Prévisualisation ponctuelle (single frame)
- Capture optimisée pour la qualité maximale

---

## 📋 Workflow Recommandé

### Étape 1: Mode Preview - Ajuster Tous les Paramètres

```
1. Sélectionner "🎥 Preview Mode"
2. Cliquer "🔌 Connect"
3. Cliquer "▶️ Start Live Preview"
4. Ajuster les paramètres:
   ├─ Focus (manuel ou auto-scan)
   ├─ Exposition (auto ou manuel)
   ├─ Luminosité
   ├─ Contraste
   └─ Saturation
5. Observer le score de netteté (sharpness)
6. Viser un score > 200 pour une bonne netteté
```

**Avantages en Mode Preview:**
- ✅ Prévisualisation très fluide (10 FPS)
- ✅ Changements visibles en temps réel
- ✅ Réglage précis du focus
- ✅ Pas de latence
- ✅ Ajustement facile de tous les paramètres

---

### Étape 2: Mode Scan - Capturer en Haute Qualité

```
1. Une fois satisfait des réglages en Preview Mode
2. Cliquer "🔄 Disconnect"
3. Sélectionner "📸 Scan Mode"
4. Choisir la qualité:
   • 4K UHD (3840x2160) - Bon compromis
   • Ultra HQ (4000x3000) - Qualité maximale
5. Cliquer "🔌 Connect"
6. Optionnel: "📸 Capture Single Frame" pour vérifier
7. Cliquer "📸 Capture High-Quality Scan"
```

**Avantages en Mode Scan:**
- ✅ Résolution maximale
- ✅ Qualité d'image optimale
- ✅ Parfait pour OCR de petits composants
- ✅ Capture des détails fins
- ✅ Fichiers haute résolution

---

## 🔄 Différences entre les Modes

| Aspect | 🎥 Preview Mode | 📸 Scan Mode |
|--------|----------------|--------------|
| **Résolution** | 1280x720 @ 60fps (fixe) | 4K ou Ultra HQ (au choix) |
| **Vitesse** | Très rapide | Plus lent |
| **Prévisualisation** | Continue, fluide (10 FPS) | Ponctuelle (single frame) |
| **Usage** | Ajustement de tous les paramètres | Capture haute qualité |
| **Fluidité** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Qualité Capture** | ⭐⭐⭐ Standard | ⭐⭐⭐⭐⭐ Maximale |
| **Temps de Capture** | ~17ms | 4K: ~100ms, UHQ: ~143ms |
| **Fichier** | Plus petit | Plus grand |
| **OCR** | Basique | Excellente |

---

## 💡 Cas d'Usage

### Scénario 1: Analyse de PCB avec Composants Petits

```
Workflow optimal:

1. 🎥 Preview Mode:
   - Ajuster le focus jusqu'à score > 250
   - Activer Auto Exposure
   - Si nécessaire, ajuster manuellement
   - Cadrer le PCB parfaitement
   
2. 📸 Scan Mode - Ultra HQ:
   - Capturer en 4000x3000
   - Meilleure qualité pour OCR
   - Identifier même les petits marquages
```

**Résultat:** Détails maximaux pour l'OCR des références de composants

---

### Scénario 2: Inspection Rapide de Carte

```
Workflow rapide:

1. 🎥 Preview Mode:
   - Ajuster rapidement le focus
   - Vérifier l'éclairage
   - Capturer directement en 720p
   
Ou si plus de qualité nécessaire:

2. 📸 Scan Mode - 4K:
   - Capturer en 3840x2160
   - Bon compromis qualité/vitesse
```

**Résultat:** Inspection efficace avec qualité suffisante

---

### Scénario 3: Documentation de Carte Complexe

```
Workflow complet:

1. 🎥 Preview Mode:
   - Trouver le focus optimal
   - Ajuster l'exposition pour éviter les reflets
   - Optimiser le contraste
   
2. 📸 Scan Mode - Ultra HQ:
   - Capturer plusieurs angles
   - Documenter chaque zone en haute qualité
   - Archives de référence
```

**Résultat:** Documentation professionnelle haute qualité

---

## 🎨 Interface Utilisateur

### Mode Preview - Interface

```
┌─────────────────────────────────────────────┐
│ 📷 Camera Mode Selection                    │
├─────────────────────────────────────────────┤
│ ⦿ 🎥 Preview Mode (720p@60fps - Fast)      │
│ ○ 📸 Scan Mode (4K/Ultra HQ)                │
│                                             │
│ ✅ Preview Mode Active                      │
│ Resolution: 1280x720 @ 60fps                │
│ Optimal for adjustments                     │
├─────────────────────────────────────────────┤
│ Camera Index: [0]                           │
│ ✅ Fixed Resolution: 1280x720 @ 60fps       │
│    (optimized for smooth preview)           │
├─────────────────────────────────────────────┤
│ [🔌 Connect] [🔄 Disconnect] [ℹ️ Info]     │
├─────────────────────────────────────────────┤
│ 🎯 Focus Control                            │
│ Focus Value: [━━━●━━━━━━━━━━━━] (0-1023)   │
│ [📍 Near] [📍 Mid] [📍 Far] [🔍 Auto]      │
├─────────────────────────────────────────────┤
│ 🎨 Image Quality Controls                   │
│ ☑ Auto Exposure                             │
│ Brightness: [━━━━━━━●━━━━━━━━━] (0-255)   │
│ Contrast:   [━━━━━━━●━━━━━━━━━] (0-255)   │
│ Saturation: [━━━━━━━●━━━━━━━━━] (0-255)   │
├─────────────────────────────────────────────┤
│ 👁️ Live Preview (Preview Mode)             │
│ [▶️ Start Live Preview]                     │
│ Refresh Rate: [━●━━━] 0.1s (10 FPS)        │
│                                             │
│ 🔴 Live preview active                      │
│ [Live camera feed here...]                  │
│ Sharpness: 245.67                           │
├─────────────────────────────────────────────┤
│ 📸 Quick Capture (Preview Quality)          │
│ 💡 Tip: For high-quality scans,             │
│    switch to Scan Mode above                │
│ JPEG Quality: [━━━━━━━━━━●] (95)           │
│ [📸 Capture Photo]                          │
└─────────────────────────────────────────────┘
```

---

### Mode Scan - Interface

```
┌─────────────────────────────────────────────┐
│ 📷 Camera Mode Selection                    │
├─────────────────────────────────────────────┤
│ ○ 🎥 Preview Mode (720p@60fps - Fast)      │
│ ⦿ 📸 Scan Mode (4K/Ultra HQ)                │
│                                             │
│ ✅ Scan Mode Active                         │
│ High quality capture mode                   │
│ Choose resolution below                     │
├─────────────────────────────────────────────┤
│ Camera Index: [0]                           │
│ Scan Quality:                               │
│ ⦿ 4K UHD (3840x2160 @ 10fps)               │
│ ○ Ultra HQ (4000x3000 @ 7fps)              │
│                                             │
│ ℹ️ Resolution: 3840x2160 @ 10fps (4K UHD)  │
├─────────────────────────────────────────────┤
│ [🔌 Connect] [🔄 Disconnect] [ℹ️ Info]     │
├─────────────────────────────────────────────┤
│ 🎯 Focus Control                            │
│ Focus Value: [━━━●━━━━━━━━━━━━] (0-1023)   │
│ [📍 Near] [📍 Mid] [📍 Far] [🔍 Auto]      │
├─────────────────────────────────────────────┤
│ 🎨 Image Quality Controls                   │
│ ☑ Auto Exposure                             │
│ Brightness: [━━━━━━━●━━━━━━━━━] (0-255)   │
│ Contrast:   [━━━━━━━●━━━━━━━━━] (0-255)   │
│ Saturation: [━━━━━━━●━━━━━━━━━] (0-255)   │
├─────────────────────────────────────────────┤
│ 👁️ Single Frame Preview (Scan Mode)        │
│ [📸 Capture Single Frame]                   │
│                                             │
│ 📸 Scan Mode - Use single frame preview     │
│    to verify, then capture high-quality     │
│    image below                              │
├─────────────────────────────────────────────┤
│ 📸 High-Quality Scan Capture                │
│ ✅ Scan Mode Active - High quality!         │
│ JPEG Quality: [━━━━━━━━━━●] (95)           │
│ [📸 Capture High-Quality Scan]              │
└─────────────────────────────────────────────┘
```

---

## ⚙️ Configuration Technique

### Preview Mode - Paramètres

```python
Mode: Preview
Resolution: 1280x720
FPS: 60
Refresh Rate: 0.1s (10 FPS)
Buffer: Minimal
Latency: ~17ms per frame
Purpose: Real-time adjustments
```

**Optimisations:**
- Résolution fixe pour performance maximale
- 60 FPS caméra pour fluidité
- Refresh 10 FPS pour équilibre CPU/fluidité
- Latence minimale pour feedback immédiat

---

### Scan Mode - Paramètres

#### Option 1: 4K UHD
```python
Mode: Scan
Resolution: 3840x2160
FPS: 10
Refresh: Single frame only
Latency: ~100ms per frame
Purpose: High quality capture
File Size: ~3-5 MB (JPEG 95)
```

#### Option 2: Ultra High Quality
```python
Mode: Scan
Resolution: 4000x3000
FPS: 7
Refresh: Single frame only
Latency: ~143ms per frame
Purpose: Maximum quality capture
File Size: ~5-8 MB (JPEG 95)
```

**Optimisations:**
- Résolution maximale pour détails
- Single frame preview économise CPU
- JPEG quality 95 pour meilleur compromis
- Focus hérité du mode Preview

---

## 📊 Comparaison de Performance

### Temps de Workflow

**Ancien Workflow (mode unique):**
```
1. Connecter en 720p
2. Ajuster focus/exposition (avec preview fluide)
3. Déconnecter
4. Changer résolution à 4K ou Ultra HQ
5. Reconnecter
6. Réajuster focus (sans preview fluide!)
7. Capturer

Temps total: ~3-5 minutes
Problèmes: Perte de settings, réajustements difficiles
```

**Nouveau Workflow (deux modes):**
```
Mode Preview:
1. Sélectionner Preview Mode
2. Connecter
3. Ajuster tous les paramètres (preview fluide)
4. Déconnecter

Mode Scan:
5. Sélectionner Scan Mode + qualité
6. Connecter (settings préservés!)
7. Vérifier avec single frame
8. Capturer

Temps total: ~1-2 minutes
Avantages: Settings préservés, workflow clair
```

**Gain de temps:** 50-60% plus rapide

---

## 🎓 Conseils et Astuces

### Pour une Qualité Maximale

1. **Toujours commencer en Preview Mode**
   - Ajuster le focus jusqu'à score > 200
   - Optimiser l'exposition
   - Vérifier le cadrage

2. **Utiliser Auto Exposure d'abord**
   - Laisser la caméra s'adapter
   - Affiner manuellement si nécessaire

3. **Observer le Score de Netteté**
   - Score > 200: Acceptable
   - Score > 250: Bon
   - Score > 300: Excellent

4. **Passer en Scan Mode pour la capture finale**
   - Ultra HQ pour OCR de précision
   - 4K pour bon compromis

---

### Optimisation de l'Éclairage

**En Preview Mode:**
- Ajuster brightness/contrast en temps réel
- Observer les reflets immédiatement
- Tester différentes positions

**En Scan Mode:**
- Les réglages d'éclairage sont préservés
- Vérifier avec single frame
- Capturer avec confiance

---

### Gestion du Focus

**Preview Mode - Focus Dynamique:**
```
1. Activer Live Preview
2. Utiliser le slider de focus
3. Observer les changements en temps réel
4. Score de netteté mis à jour en continu
5. Trouver le pic de netteté
```

**Scan Mode - Focus Statique:**
```
1. Focus déjà optimisé en Preview Mode
2. Valeur préservée lors du changement de mode
3. Vérification optionnelle avec single frame
4. Capture avec focus optimal
```

---

## 🔧 Troubleshooting

### Problème: Preview Saccadé en Preview Mode

**Solutions:**
1. Vérifier que Preview Mode est sélectionné (720p@60fps)
2. Réduire refresh rate si CPU lent
3. Fermer autres applications
4. Vérifier connexion USB 3.0

---

### Problème: Image Floue en Scan Mode

**Solutions:**
1. Retourner en Preview Mode
2. Réajuster le focus avec live preview
3. Viser score > 250
4. Revenir en Scan Mode
5. Capturer à nouveau

---

### Problème: Changement de Mode ne Fonctionne Pas

**Solutions:**
1. Toujours déconnecter avant de changer de mode
2. Sélectionner nouveau mode
3. Reconnecter
4. Les settings sont préservés

---

## 📚 Résumé des Avantages

### Mode Preview
✅ Prévisualisation fluide (10 FPS)
✅ Ajustements en temps réel
✅ Focus facile à optimiser
✅ Tous les contrôles disponibles
✅ Feedback immédiat
✅ Pas de latence

### Mode Scan
✅ Qualité maximale
✅ Choix de résolution
✅ Settings préservés du Preview
✅ Optimisé pour OCR
✅ Fichiers haute résolution
✅ Captures professionnelles

### Workflow Global
✅ 50% plus rapide
✅ Workflow intuitif
✅ Séparation claire des tâches
✅ Moins d'erreurs
✅ Meilleurs résultats
✅ Expérience utilisateur améliorée

---

**Version:** 2.0  
**Date:** 2026-02-17  
**Système:** Deux Modes (Preview + Scan)  
**Caméra:** Arducam 108MP USB 3.0 (B0494C)
