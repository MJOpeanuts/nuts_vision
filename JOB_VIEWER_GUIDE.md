# Job Viewer Feature - User Guide

## Aperçu / Overview

**Français:**
Le visualiseur de tâches ("Job Viewer") est une nouvelle fonctionnalité de l'interface web nuts_vision qui permet de visualiser chaque job sauvegardé avec:
- L'image d'origine complète
- Chaque image IC croppée (découpée)
- Les résultats OCR associés à chaque composant

**English:**
The Job Viewer is a new feature in the nuts_vision web interface that allows you to view each saved job with:
- The complete original image
- Each cropped IC image
- The associated OCR results for each component

---

## Accès / Access

**Navigation:** Utilisez le menu latéral → **🔍 Job Viewer** / Use the sidebar menu → **🔍 Job Viewer**

---

## Fonctionnalités / Features

### 1. Sélection de Job / Job Selection

**Interface:**
- Menu déroulant montrant tous les jobs traités / Dropdown menu showing all processed jobs
- Format: `Job ID - Nom_fichier (N détections)` / Format: `Job ID - Filename (N detections)`
- Triés par date (plus récent en premier) / Sorted by date (most recent first)

### 2. Informations sur le Job / Job Information

**Métriques affichées / Displayed Metrics:**
- **Job ID**: Identifiant unique du job / Unique job identifier
- **Détections**: Nombre total de composants détectés / Total number of detected components
- **Started**: Horodatage de début / Start timestamp
- **Ended**: Horodatage de fin ou "Running" si incomplet / End timestamp or "Running" if incomplete

### 3. Image Originale / Original Image

**Affichage / Display:**
- Image PCB complète telle que téléchargée / Complete PCB image as uploaded
- Légende avec le nom de fichier / Caption with filename
- Message d'avertissement si le fichier n'existe plus / Warning message if file not found

### 4. Composants IC Croppés / Cropped IC Components

Pour chaque composant IC / For each IC component:

#### Colonne Gauche / Left Column:
- **Image croppée**: Composant découpé / **Cropped image**: Cut out component
- **Bounding box**: Coordonnées (X1, Y1, X2, Y2) / **Bounding box**: Coordinates (X1, Y1, X2, Y2)

#### Colonne Droite / Right Column:
- **MPN**: Numéro de pièce fabricant (surligné en vert si extrait) / Manufacturer Part Number (highlighted in green if extracted)
- **Texte OCR brut**: Texte complet reconnu par Tesseract / **Raw OCR Text**: Complete text recognized by Tesseract
- **Angle de rotation**: Orientation utilisée pour l'OCR (0°, 90°, 180°, 270°) / **Rotation angle**: Orientation used for OCR (0°, 90°, 180°, 270°)
- **Horodatage traitement**: Quand l'OCR a été effectué / **Processing timestamp**: When OCR was performed
- **Chemin fichier**: Emplacement complet de l'image croppée / **File path**: Full path to cropped image

### 5. Statistiques Résumées / Summary Statistics

**Panneau inférieur affichant / Bottom panel displaying:**
- **Total ICs**: Nombre de composants croppés / Count of cropped components
- **OCR Traités**: Combien ont eu l'OCR effectué / How many had OCR performed
- **MPNs Extraits**: Extractions réussies / Successful extractions
- **Taux de Réussite**: Pourcentage d'extractions réussies / Success rate percentage

---

## Cas d'Utilisation / Use Cases

### 1. Contrôle Qualité / Quality Control
Vérifier la précision de la détection et de l'OCR pour chaque job traité.
/ Review detection and OCR accuracy for each processed job.

### 2. Débogage / Debugging
Identifier les problèmes avec des détections spécifiques de composants.
/ Identify issues with specific component detections.

### 3. Documentation
Exporter ou réviser les résultats traités avec preuve visuelle.
/ Export or review processed results with visual proof.

### 4. Révision des Données d'Entraînement / Training Data Review
Vérifier les résultats pour l'amélioration du modèle.
/ Verify results for model improvement.

### 5. Rapports Client / Client Reporting
Montrer les résultats de traitement avec preuve visuelle.
/ Show processing results with visual proof.

---

## Guide Pas-à-Pas / Step-by-Step Guide

### Étape 1 / Step 1: Naviguer vers Job Viewer
1. Ouvrez l'interface web nuts_vision / Open the nuts_vision web interface
2. Cliquez sur **🔍 Job Viewer** dans le menu latéral / Click **🔍 Job Viewer** in the sidebar menu

### Étape 2 / Step 2: Sélectionner un Job
1. Utilisez le menu déroulant "Select a Job" / Use the "Select a Job" dropdown
2. Choisissez le job que vous souhaitez visualiser / Choose the job you want to view
3. Les informations du job s'afficheront automatiquement / Job information will display automatically

### Étape 3 / Step 3: Examiner l'Image Originale
1. Faites défiler jusqu'à "📸 Original Image" / Scroll to "📸 Original Image"
2. Visualisez l'image PCB complète / View the complete PCB image

### Étape 4 / Step 4: Explorer les Composants IC
1. Faites défiler jusqu'à "✂️ Cropped IC Components" / Scroll to "✂️ Cropped IC Components"
2. Cliquez sur chaque section extensible pour voir les détails / Click each expandable section to see details
3. Examinez l'image croppée et les résultats OCR côte à côte / Review cropped image and OCR results side-by-side

### Étape 5 / Step 5: Vérifier les Statistiques
1. Faites défiler jusqu'au panneau "📊 Summary" / Scroll to the "📊 Summary" panel
2. Vérifiez le taux de réussite global de l'OCR / Check the overall OCR success rate

---

## Dépannage / Troubleshooting

### Problème: "Database not connected" / Issue: "Database not connected"
**Solution:**
```bash
# Démarrer PostgreSQL avec Docker / Start PostgreSQL with Docker
docker-compose up -d
```

### Problème: "No jobs found" / Issue: "No jobs found"
**Solution:**
Traitez d'abord quelques images via la page "📤 Upload & Process".
/ Process some images first via the "📤 Upload & Process" page.

### Problème: "Original image not found" / Issue: "Original image not found"
**Cause possible / Possible cause:**
Le fichier image a été déplacé ou supprimé après le traitement.
/ The image file was moved or deleted after processing.

### Problème: "Cropped image not found" / Issue: "Cropped image not found"
**Cause possible / Possible cause:**
Les fichiers de sortie ont été nettoyés ou déplacés.
/ Output files were cleaned up or moved.

**Solution:**
Vérifiez le répertoire `outputs/cropped_components/`.
/ Check the `outputs/cropped_components/` directory.

---

## Améliorations Futures Possibles / Possible Future Enhancements

1. **Bouton de téléchargement** pour exporter les données du job en lot / **Download button** for batch export of job data
2. **Comparaison côte à côte** de plusieurs jobs / **Side-by-side comparison** of multiple jobs
3. **Annotations/notes** sur des composants spécifiques / **Annotations/notes** on specific components
4. **Re-exécuter l'OCR** sur des composants individuels / **Re-run OCR** on individual components
5. **Export vers rapport PDF** / **Export to PDF report**

---

## Support Technique / Technical Support

Pour toute question ou problème:
/ For any questions or issues:

- Consultez la documentation complète dans le dépôt / Check the full documentation in the repository
- Créez une issue sur GitHub / Create an issue on GitHub
- Contactez l'équipe de développement / Contact the development team

---

**Version**: 1.0.0  
**Date**: Février 2026  
**Auteur / Author**: nuts_vision Team
