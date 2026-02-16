# Guide Visuel - nuts_vision

## Workflow Complet en 3 Étapes

```
┌─────────────────────────────────────────────────────────────────┐
│                    ÉTAPE 1 : INSTALLATION                        │
│                         (5 minutes)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌──────────────────────┐
                  │ Installer Tesseract  │
                  │ (OCR logiciel)       │
                  └──────────────────────┘
                              │
                              ▼
                  ┌──────────────────────┐
                  │ pip install -r       │
                  │ requirements.txt     │
                  └──────────────────────┘
                              │
                              ▼
                  ┌──────────────────────┐
                  │ python               │
                  │ check_dependencies.py│
                  └──────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              ÉTAPE 2 : ENTRAÎNER LE MODÈLE                       │
│                  (30 min - 2 heures)                             │
│            (Une seule fois, puis réutilisable)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
           ┌─────────────────────────────────────┐
           │ Télécharger le dataset CompDetect   │
           │ (583 images annotées)                │
           └─────────────────────────────────────┘
                              │
                              ▼
           ┌─────────────────────────────────────┐
           │ python src/train.py                 │
           │ --data data.yaml --epochs 100       │
           └─────────────────────────────────────┘
                              │
                              ▼
           ┌─────────────────────────────────────┐
           │ Modèle entraîné sauvegardé :        │
           │ runs/detect/component_detector/     │
           │      weights/best.pt                │
           └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│           ÉTAPE 3 : ANALYSER UNE PHOTO DE CARTE                  │
│                    (30 secondes)                                 │
│              (Répétable à l'infini)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Votre photo      │
                    │ ma_carte.jpg     │
                    └──────────────────┘
                              │
                              ▼
           ┌─────────────────────────────────────┐
           │ python test_simple.py               │
           │ --model best.pt --image ma_carte.jpg│
           └─────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Résultats :      │
                    │ - Image annotée  │
                    │ - Liste JSON     │
                    └──────────────────┘
```

## Que Fait le Système ?

```
Photo de carte électronique
         │
         ▼
┌────────────────────┐
│  1. DÉTECTION      │ ← YOLOv8 trouve les composants
│                    │
│  Input:  [Image]   │
│  Output: [Boîtes]  │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  2. DÉCOUPAGE      │ ← Extraction des composants individuels
│                    │
│  Input:  [Boîtes]  │
│  Output: [Images]  │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  3. OCR            │ ← Tesseract lit le texte sur les ICs
│                    │
│  Input:  [Images]  │
│  Output: [Texte]   │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  RÉSULTATS         │
│  - CSV avec MPNs   │
│  - Images découpées│
│  - Statistiques    │
└────────────────────┘
```

## Types de Composants Détectés

```
┌─────────────────────────────────────────────────────────────┐
│                  16 CLASSES DE COMPOSANTS                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🔲 IC (Circuit Intégré)    🔲 LED                          │
│  🔲 Batterie                🔲 Buzzer                        │
│  🔲 Condensateur            🔲 Horloge                       │
│  🔲 Connecteur              🔲 Diode                         │
│  🔲 Affichage               🔲 Fusible                       │
│  🔲 Inductance              🔲 Potentiomètre                 │
│  🔲 Relais                  🔲 Résistance                    │
│  🔲 Interrupteur            🔲 Transistor                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Structure des Fichiers de Sortie

```
outputs/
│
├── results/
│   ├── ma_carte_detected.jpg      ← Image avec rectangles colorés
│   ├── detections.json             ← Liste de tous les composants
│   └── mpn_results.csv             ← Numéros de pièce extraits
│
├── cropped_components/
│   ├── ma_carte_IC_0.jpg           ← Composant IC numéro 0
│   ├── ma_carte_IC_1.jpg           ← Composant IC numéro 1
│   ├── ma_carte_resistor_0.jpg     ← Résistance numéro 0
│   └── ...                         ← etc.
│
└── visualizations/
    ├── detection_statistics.png    ← Graphiques
    └── ocr_results.png             ← Statistiques OCR
```

## Exemple de Résultat JSON

```json
{
  "class_name": "IC",
  "confidence": 0.95,
  "bbox": [100, 150, 200, 250],
  "component_info": {
    "type": "Integrated Circuit",
    "position": "center-left"
  }
}
```

## Exemple de CSV avec MPNs

```
┌────────────────────────────────────────────────────────────┐
│ image_path              │ component_type │ mpn            │
├─────────────────────────┼────────────────┼────────────────┤
│ outputs/.../IC_0.jpg    │ IC             │ LM358N         │
│ outputs/.../IC_1.jpg    │ IC             │ 74HC595        │
│ outputs/.../IC_2.jpg    │ IC             │ ATmega328P     │
└────────────────────────────────────────────────────────────┘
```

## Commandes Principales

### 1️⃣ Test Simple (Le plus rapide)
```bash
python test_simple.py --model best.pt --image ma_carte.jpg
```
→ Détecte et annote l'image

### 2️⃣ Pipeline Complet (Tout faire)
```bash
python src/pipeline.py --model best.pt --image ma_carte.jpg
```
→ Détection + Découpage + OCR + Visualisations

### 3️⃣ Détection Seule (Sans OCR)
```bash
python src/detect.py --model best.pt --image ma_carte.jpg
```
→ Juste la détection, pas d'OCR

### 4️⃣ Plusieurs Images
```bash
python src/pipeline.py --model best.pt --image-dir mes_cartes/
```
→ Traite tout un dossier

## Paramètres Utiles

```
--conf 0.3          Seuil de confiance (0.0 à 1.0)
                    ↓ Plus bas = plus de détections
                    ↑ Plus haut = plus précis

--no-ocr            Désactiver l'extraction de texte
                    (plus rapide)

--no-viz            Désactiver les graphiques
                    (plus rapide)

--padding 20        Marge autour des composants découpés
                    (en pixels)
```

## Temps de Traitement Typiques

```
Installation             : 5 minutes
Téléchargement dataset   : 5-10 minutes
Entraînement (nano)      : 30 minutes (GPU) / 2h (CPU)
Entraînement (medium)    : 1-2 heures (GPU) / 4-6h (CPU)
Détection (1 image)      : 1-2 secondes
OCR (1 composant)        : 0.5-1 seconde
Pipeline complet (1 img) : 10-30 secondes
```

## Configuration Matérielle Recommandée

### Minimum
- CPU : Processeur moderne (Intel i5 ou équivalent)
- RAM : 8 GB
- Disque : 5 GB libre
- GPU : Optionnel (mais 10-100x plus rapide)

### Recommandé
- CPU : Intel i7 / AMD Ryzen 7 ou supérieur
- RAM : 16 GB ou plus
- Disque : SSD avec 10 GB libre
- GPU : NVIDIA avec 4 GB VRAM (ex: GTX 1650 ou supérieur)

## Ressources

- 📘 [DEMARRAGE_RAPIDE.md](DEMARRAGE_RAPIDE.md) - Instructions détaillées
- 📗 [README_FR.md](README_FR.md) - Documentation complète
- 📙 [COMMENCER_ICI.md](COMMENCER_ICI.md) - Guide ultra-rapide
- 💻 [test_simple.py](test_simple.py) - Script de test facile

---

Créé avec ❤️ pour faciliter l'analyse de cartes électroniques
