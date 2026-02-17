# Usage Examples for nuts_vision with Database Integration

This document provides practical examples of using nuts_vision with the enhanced OCR and database tracking features.

## Basic Usage (Without Database)

### Process a Single Image

```bash
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image test_board.jpg
```

This will:
- Detect all components in the image
- Crop only IC components
- Run OCR with 4 rotations (0°, 90°, 180°, 270°) to find the best angle
- Generate results in `outputs/`

### Process Multiple Images

```bash
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image-dir images/
```

## Advanced Usage with Database

### 1. Start the Database

```bash
docker-compose up -d
```

### 2. Run Pipeline with Database Logging

```bash
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image test_board.jpg \
  --use-database
```

This will log all operations to PostgreSQL:
- Image upload information
- Detection job with start/end times
- All component detections
- Cropped IC images
- OCR results with rotation angles and confidence scores

### 3. Query the Database

```bash
# Connect to database
docker exec -it nuts_vision_db psql -U nuts_user -d nuts_vision

# View recent jobs
SELECT j.job_id, i.file_name, j.started_at, j.ended_at 
FROM log_jobs j
JOIN images_input i ON j.image_id = i.image_id
ORDER BY j.started_at DESC
LIMIT 10;

# View OCR results with rotation info
SELECT o.cleaned_mpn, o.rotation_angle, o.confidence, ic.cropped_file_path
FROM ics_ocr o
JOIN ics_cropped ic ON o.cropped_id = ic.cropped_id
ORDER BY o.processed_at DESC;
```

## Individual Components

### Detection Only

```bash
python src/detect.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image board.jpg \
  --conf 0.3
```

### Crop Only ICs

```bash
# From detection results file
python src/crop.py \
  --detection-file outputs/results/detections.json \
  --output-dir outputs/cropped_ics \
  --filter IC
```

### OCR Only

The OCR now automatically tries 4 rotation angles and picks the best result:

```bash
python src/ocr.py \
  --image-dir outputs/cropped_ics \
  --output-csv outputs/mpn_results.csv \
  --filter IC
```

Output will show:
```
Processing: board_IC_0.jpg
  MPN: LM358N (angle: 0°, conf: 92.3)
Processing: board_IC_1.jpg
  MPN: 74HC595 (angle: 90°, conf: 87.5)
```

## OCR Improvements

The enhanced OCR process:

1. **Image Optimization**:
   - Resizes small images to minimum 100x100 pixels
   - Applies CLAHE contrast enhancement
   - Denoises and sharpens the image
   - Tries multiple preprocessing methods

2. **Multi-Angle Detection**:
   - Rotates image at 0°, 90°, 180°, 270°
   - Runs OCR at each angle
   - Selects the result with highest confidence

3. **Better Accuracy**:
   - Tracks which angle worked best
   - Reports confidence scores
   - Stores rotation angle in database

## Example: Complete Workflow

```bash
# 1. Start database
docker-compose up -d

# 2. Process a batch of circuit boards
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image-dir production_boards/ \
  --use-database \
  --conf 0.4

# 3. Query results
docker exec -it nuts_vision_db psql -U nuts_user -d nuts_vision -c "
SELECT 
    i.file_name,
    COUNT(DISTINCT d.detection_id) as total_components,
    COUNT(DISTINCT ic.cropped_id) as ics_found,
    COUNT(DISTINCT o.ocr_id) FILTER (WHERE o.cleaned_mpn != '') as mpns_extracted
FROM images_input i
JOIN log_jobs j ON i.image_id = j.image_id
LEFT JOIN detections d ON j.job_id = d.job_id
LEFT JOIN ics_cropped ic ON j.job_id = ic.job_id
LEFT JOIN ics_ocr o ON ic.cropped_id = o.cropped_id
GROUP BY i.file_name
ORDER BY i.upload_at DESC;
"

# 4. Export results
docker exec -it nuts_vision_db psql -U nuts_user -d nuts_vision -c "
COPY (
    SELECT 
        i.file_name,
        o.cleaned_mpn,
        o.rotation_angle,
        o.confidence,
        o.processed_at
    FROM ics_ocr o
    JOIN ics_cropped ic ON o.cropped_id = ic.cropped_id
    JOIN log_jobs j ON o.job_id = j.job_id
    JOIN images_input i ON j.image_id = i.image_id
    WHERE o.cleaned_mpn != ''
    ORDER BY o.processed_at DESC
) TO STDOUT WITH CSV HEADER;
" > all_mpns.csv

# 5. Stop database when done
docker-compose down
```

## Filtering by Component Type

### Crop Only Specific Components

```bash
# Crop only ICs
python src/crop.py \
  --detection-file outputs/results/detections.json \
  --filter IC

# Crop ICs and LEDs
python src/crop.py \
  --detection-file outputs/results/detections.json \
  --filter IC LED
```

### OCR Only Specific Components

```bash
# OCR only ICs (default)
python src/ocr.py \
  --image-dir outputs/cropped_components \
  --filter IC

# OCR both ICs and displays
python src/ocr.py \
  --image-dir outputs/cropped_components \
  --filter IC Display
```

## Environment Configuration

Create a `.env` file for custom database settings:

```bash
cp .env.example .env
```

Edit `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nuts_vision
DB_USER=nuts_user
DB_PASSWORD=your_secure_password
```

## Troubleshooting

### OCR Returns Empty Results

If OCR is not finding text:
1. Check that cropped images are clear and readable
2. The new multi-angle OCR should help with rotated text
3. Try adjusting the confidence threshold for detections
4. Ensure Tesseract is properly installed: `tesseract --version`

### Database Connection Failed

If pipeline cannot connect to database:
```bash
# Check if container is running
docker-compose ps

# View logs
docker-compose logs postgres

# Test connection
docker exec -it nuts_vision_db psql -U nuts_user -d nuts_vision -c "SELECT 1;"
```

### No ICs Detected

If no IC components are being cropped:
1. Check detection results in `outputs/results/detections.json`
2. Lower the confidence threshold: `--conf 0.2`
3. Verify the model is properly trained for IC detection

## Performance Tips

1. **Batch Processing**: Process multiple images at once with `--image-dir`
2. **Confidence Threshold**: Adjust `--conf` to balance precision/recall
3. **Skip Visualizations**: Use `--no-viz` for faster processing
4. **Database**: Only use `--use-database` when you need tracking
5. **Parallel Processing**: Process different image batches in parallel

## Example Output

```
============================================================
ELECTRONIC COMPONENT ANALYSIS PIPELINE
Database logging: ENABLED
============================================================

[STEP 1/4] Running component detection on board.jpg...
------------------------------------------------------------
Detected 15 components

[STEP 2/4] Cropping IC components for OCR...
------------------------------------------------------------
Cropped 3 IC components from board.jpg

[STEP 3/4] Extracting MPNs using OCR...
------------------------------------------------------------
  board_IC_0.jpg: LM358N (angle: 0°)
  board_IC_1.jpg: 74HC595 (angle: 90°)
  board_IC_2.jpg: ATmega328P (angle: 0°)

[STEP 3/4] Compiling OCR results...
------------------------------------------------------------
Found 3 images to process
Processing: board_IC_0.jpg
  MPN: LM358N (angle: 0°, conf: 92.3)
Processing: board_IC_1.jpg
  MPN: 74HC595 (angle: 90°, conf: 87.5)
Processing: board_IC_2.jpg
  MPN: ATmega328P (angle: 0°, conf: 95.1)

Extracted MPNs: 3/3

[STEP 4/4] Creating visualizations...
------------------------------------------------------------

============================================================
PIPELINE COMPLETE!
============================================================

Results saved to: outputs
  - Detections: outputs/results
  - Cropped IC components: outputs/cropped_components
  - MPN extraction: outputs/results/mpn_results.csv
  - Visualizations: outputs/visualizations
  - Database: Logged to PostgreSQL
```
