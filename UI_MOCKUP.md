# Interface Utilisateur - Aperçu de la Prévisualisation en Direct
# User Interface - Live Preview Overview

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                   🔧 nuts_vision - Camera Control Page                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ 🔌 Camera Connection                                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Camera Index: [0        ▼]                    ┌─────────────────────────┐   │
│                                               │ Status:                 │   │
│ Resolution Preset:                            │ ✅ Connected            │   │
│ [Full HD (1920x1080) - Recommended ▼]         │                         │   │
│                                               │ Resolution: 1920x1080   │   │
│ 📐 Resolution: 1920x1080 @ 30fps              │ FPS: 30                 │   │
│                                               │ Focus: 125              │   │
│ [🔌 Connect]  [🔄 Disconnect]  [ℹ️ Info]      └─────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 🎯 Focus Control                                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Adjust the camera focus manually using the slider below, or use auto-focus  │
│ to automatically find the optimal focus value.                              │
│ **Tip:** Enable live preview above to see focus changes in real-time!       │
│                                                                              │
│ Focus Value:                                   Auto Focus                    │
│ [━━━━━━━━●━━━━━━━━━━] 125                                                    │
│ 0                    255                       [🔍 Auto Focus Scan]          │
│                                                                              │
│                                                Focus Presets                 │
│                                                [📍 Near] [📍 Mid] [📍 Far]   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 👁️ Live Preview                                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Use live preview to adjust focus in real-time. The preview will             │
│ continuously update to show the current camera view, making it easier to    │
│ find the optimal focus setting.                                             │
│                                                                              │
│ [▶️ Start Live Preview]  [📸 Capture Single Frame]                          │
│                                                                              │
│ Refresh Rate: [━●━━━━━━━━] 0.5s (2.0 FPS)                                   │
│               0.1s  0.3s  0.5s  1.0s  2.0s                                  │
│                                                                              │
│ 🔴 Live preview is running. Adjust focus slider above to see changes        │
│    in real-time.                                                            │
│                                                                              │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │                                                                        │ │
│ │                        [CAMERA LIVE FEED]                              │ │
│ │                                                                        │ │
│ │                     Real-time camera preview                           │ │
│ │                    showing circuit board with                          │ │
│ │                    electronic components                               │ │
│ │                                                                        │ │
│ │                                                                        │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│ Live Preview - Sharpness: 245.67 (higher is sharper)                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 📸 Capture Photo                                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ JPEG Quality: [━━━━━━━━━━━━━━━━●━━] 95                                      │
│               50              75              100                            │
│                                                                              │
│ Custom Save Path (optional):                                                │
│ [Leave empty for auto-generated path                           ]            │
│                                                                              │
│ Actions:                                                                     │
│ [📸 Capture Photo]                                                           │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 🔄 Process Captured Photo                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ ℹ️ Last captured photo: outputs/camera_captures/arducam_20260217_113307.jpg │
│                                                                              │
│ Process the captured photo through the nuts_vision pipeline to detect       │
│ components and extract manufacturer part numbers.                           │
│                                                                              │
│ [🔄 Process Image]                                                           │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Nouvelles Fonctionnalités / New Features

### 1. 📐 Presets de Résolution / Resolution Presets
- **VGA (640x480)** - Basse qualité / Low quality
- **HD (1280x720)** - Prévisualisation rapide / Fast preview
- **Full HD (1920x1080)** - Recommandé / Recommended ⭐
- **2K (2560x1440)** - Haute qualité / High quality
- **4K (3840x2160)** - Qualité max / Max quality
- **Personnalisée / Custom** - Valeurs personnalisées / Custom values

### 2. 📊 Affichage de la Résolution / Resolution Display
L'interface affiche maintenant clairement:
- Résolution actuelle (largeur x hauteur)
- FPS configuré
- Valeur de focus actuelle

The interface now clearly displays:
- Current resolution (width x height)
- Configured FPS
- Current focus value

### 3. 👁️ Prévisualisation en Direct / Live Preview
- ▶️ **Start/Stop** - Activer/Désactiver la prévisualisation
- 📸 **Capture Single Frame** - Capturer une seule image
- 🎚️ **Refresh Rate Control** - Contrôle du taux de rafraîchissement
  - 0.1s (10 FPS) - Très rapide / Very fast
  - 0.5s (2 FPS) - Équilibré / Balanced ⭐
  - 2.0s (0.5 FPS) - Économe / Conservative
- 📈 **Sharpness Score** - Score de netteté affiché en temps réel

### 4. 🎯 Presets de Focus / Focus Presets
- 📍 **Near** (~10cm) - Objets proches / Close objects
- 📍 **Mid** (~20cm) - Distance moyenne / Medium distance ⭐
- 📍 **Far** (~30cm+) - Objets éloignés / Distant objects

### 5. 🔧 Contrôle du Focus Amélioré / Improved Focus Control
- Application automatique lors du changement du curseur
- Auto-focus avec scan complet
- Feedback visuel en temps réel avec la prévisualisation

- Auto-apply on slider change
- Auto-focus with full scan
- Real-time visual feedback with live preview

## Workflow Recommandé / Recommended Workflow

### Étape 1: Connexion / Step 1: Connection
1. Sélectionner le preset de résolution (HD pour preview, Full HD pour capture)
2. Cliquer sur "Connect"
3. Vérifier les informations affichées dans le panneau "Status"

### Étape 2: Réglage du Focus / Step 2: Focus Adjustment
1. Cliquer sur "▶️ Start Live Preview"
2. Ajuster le curseur de focus tout en observant l'image
3. Observer le score de netteté (sharpness)
4. Viser un score > 200 pour une netteté optimale
5. Ou utiliser "🔍 Auto Focus Scan" pour un réglage automatique

### Étape 3: Capture / Step 3: Capture
1. Arrêter la prévisualisation (optionnel)
2. Ajuster la qualité JPEG (95 recommandé)
3. Cliquer sur "📸 Capture Photo"
4. Vérifier la photo capturée

### Étape 4: Traitement / Step 4: Processing
1. Cliquer sur "🔄 Process Image"
2. Consulter les résultats dans le "Job Viewer"

## Optimisations de Performance / Performance Optimizations

### Refresh Rate Control
Le contrôle du taux de rafraîchissement permet d'équilibrer entre:
- **Fluidité de la prévisualisation** (taux élevé = 0.1s)
- **Utilisation CPU/réseau** (taux faible = 2.0s)

The refresh rate control balances between:
- **Preview smoothness** (high rate = 0.1s)
- **CPU/network usage** (low rate = 2.0s)

**Recommandation:** 
- Pour le réglage du focus: 0.3-0.5s
- Pour économiser les ressources: 1.0-2.0s
- For focus adjustment: 0.3-0.5s
- To save resources: 1.0-2.0s

## Scores de Netteté Typiques / Typical Sharpness Scores

- **< 50** - Très flou / Very blurry ❌
- **50-100** - Flou / Blurry ⚠️
- **100-200** - Acceptable ✓
- **200-300** - Bon / Good ✓✓
- **> 300** - Excellent ✓✓✓

Pour l'OCR sur les PCB, visez un score > 150
For OCR on PCBs, aim for a score > 150
