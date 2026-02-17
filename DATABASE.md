# Database Setup for nuts_vision

This document describes the PostgreSQL database setup for tracing all image processing and extraction operations in nuts_vision.

## Database Schema

The database consists of 6 main tables that track the complete pipeline:

### 1. `images_input`
Stores information about uploaded/processed images.

| Column | Type | Description |
|--------|------|-------------|
| image_id | SERIAL PRIMARY KEY | Unique image identifier |
| file_name | VARCHAR(255) | Name of the image file |
| file_path | TEXT | Full path to the image file |
| upload_at | TIMESTAMP | Upload/processing timestamp |
| format | VARCHAR(10) | Image format (jpg, png, etc.) |

### 2. `log_jobs`
Logs detection jobs and their execution details.

| Column | Type | Description |
|--------|------|-------------|
| job_id | SERIAL PRIMARY KEY | Unique job identifier |
| image_id | INTEGER | Foreign key to images_input |
| started_at | TIMESTAMP | Job start time |
| ended_at | TIMESTAMP | Job end time |
| model | VARCHAR(255) | Model name/path used |

### 3. `detections`
Stores detection results for each job.

| Column | Type | Description |
|--------|------|-------------|
| detection_id | SERIAL PRIMARY KEY | Unique detection identifier |
| job_id | INTEGER | Foreign key to log_jobs |
| class_name | VARCHAR(50) | Component class (IC, LED, etc.) |
| confidence | FLOAT | Detection confidence score |
| bbox_x1, bbox_y1, bbox_x2, bbox_y2 | FLOAT | Bounding box coordinates |

### 4. `ics_cropped`
Links jobs to cropped IC images.

| Column | Type | Description |
|--------|------|-------------|
| cropped_id | SERIAL PRIMARY KEY | Unique cropped image identifier |
| job_id | INTEGER | Foreign key to log_jobs |
| detection_id | INTEGER | Foreign key to detections |
| cropped_file_path | TEXT | Path to cropped image |
| created_at | TIMESTAMP | Creation timestamp |

### 5. `ics_ocr`
Stores OCR results for cropped IC images.

| Column | Type | Description |
|--------|------|-------------|
| ocr_id | SERIAL PRIMARY KEY | Unique OCR result identifier |
| job_id | INTEGER | Foreign key to log_jobs |
| cropped_id | INTEGER | Foreign key to ics_cropped |
| raw_text | TEXT | Raw OCR text output |
| cleaned_mpn | VARCHAR(255) | Cleaned manufacturer part number |
| rotation_angle | INTEGER | Rotation angle used (0, 90, 180, 270) |
| confidence | FLOAT | OCR confidence score |
| processed_at | TIMESTAMP | Processing timestamp |

### 6. `camera_captures` ⭐ NEW
Stores camera captures with camera settings and metadata.

| Column | Type | Description |
|--------|------|-------------|
| capture_id | SERIAL PRIMARY KEY | Unique capture identifier |
| file_name | VARCHAR(255) | Name of captured file |
| file_path | TEXT | Full path to captured file |
| captured_at | TIMESTAMP | Capture timestamp |
| camera_mode | VARCHAR(20) | Camera mode ('preview' or 'scan') |
| resolution_width | INTEGER | Image width in pixels |
| resolution_height | INTEGER | Image height in pixels |
| fps | INTEGER | Frames per second setting |
| focus_value | INTEGER | Focus value (0-1023) |
| exposure_value | INTEGER | Exposure setting |
| brightness | INTEGER | Brightness value (0-255) |
| contrast | INTEGER | Contrast value (0-255) |
| saturation | INTEGER | Saturation value (0-255) |
| jpeg_quality | INTEGER | JPEG quality (0-100) |
| file_size_bytes | BIGINT | File size in bytes |
| notes | TEXT | Optional notes about the capture |

**Features:**
- Tracks all Arducam 108MP camera captures
- Preserves camera settings for reproducibility
- Differentiates between Preview Mode (720p@60fps) and Scan Mode (4K/Ultra HQ)
- Indexed by capture time and camera mode for fast queries

## Quick Start with Docker

### 1. Start the Database

```bash
docker-compose up -d
```

This will:
- Start a PostgreSQL 15 container
- Create the `nuts_vision` database
- Initialize all tables with the schema
- Expose the database on port 5432

### 2. Verify Database is Running

```bash
docker-compose ps
```

You should see the `nuts_vision_db` container running.

### 3. Run Pipeline with Database Logging

```bash
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image path/to/board.jpg \
  --use-database
```

## Manual Setup (Without Docker)

If you prefer to use an existing PostgreSQL installation:

### 1. Create Database

```sql
CREATE DATABASE nuts_vision;
CREATE USER nuts_user WITH PASSWORD 'nuts_password';
GRANT ALL PRIVILEGES ON DATABASE nuts_vision TO nuts_user;
```

### 2. Initialize Schema

```bash
psql -U nuts_user -d nuts_vision -f database/init.sql
```

### 3. Configure Connection

Set environment variables:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=nuts_vision
export DB_USER=nuts_user
export DB_PASSWORD=nuts_password
```

## Database Operations

### View Job Statistics

Connect to the database:

```bash
docker exec -it nuts_vision_db psql -U nuts_user -d nuts_vision
```

Query job statistics:

```sql
-- Get all jobs
SELECT j.job_id, i.file_name, j.started_at, j.ended_at, j.model
FROM log_jobs j
JOIN images_input i ON j.image_id = i.image_id
ORDER BY j.started_at DESC;

-- Get detections for a job
SELECT class_name, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2
FROM detections
WHERE job_id = 1;

-- Get OCR results with rotation angles
SELECT o.cleaned_mpn, o.rotation_angle, o.confidence, ic.cropped_file_path
FROM ics_ocr o
JOIN ics_cropped ic ON o.cropped_id = ic.cropped_id
WHERE o.job_id = 1;

-- Count components by type
SELECT class_name, COUNT(*) as count
FROM detections
GROUP BY class_name
ORDER BY count DESC;

-- Get successful MPN extractions
SELECT cleaned_mpn, rotation_angle, confidence
FROM ics_ocr
WHERE cleaned_mpn IS NOT NULL AND cleaned_mpn != ''
ORDER BY processed_at DESC;
```

### Backup Database

```bash
docker exec nuts_vision_db pg_dump -U nuts_user nuts_vision > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker exec -i nuts_vision_db psql -U nuts_user nuts_vision
```

### Stop Database

```bash
docker-compose down
```

To also remove the data volume:

```bash
docker-compose down -v
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DB_HOST | localhost | Database host |
| DB_PORT | 5432 | Database port |
| DB_NAME | nuts_vision | Database name |
| DB_USER | nuts_user | Database user |
| DB_PASSWORD | nuts_password | Database password |

## Troubleshooting

### Connection Failed

If the pipeline cannot connect to the database:

1. Check if the container is running: `docker-compose ps`
2. Check container logs: `docker-compose logs postgres`
3. Verify connection settings in environment variables
4. Test connection manually:
   ```bash
   docker exec -it nuts_vision_db psql -U nuts_user -d nuts_vision -c "SELECT 1;"
   ```

### Permission Denied

If you get permission errors:

```bash
docker exec -it nuts_vision_db psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE nuts_vision TO nuts_user;"
docker exec -it nuts_vision_db psql -U postgres -d nuts_vision -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nuts_user;"
```

### Reset Database

To completely reset the database:

```bash
docker-compose down -v
docker-compose up -d
```

## Python API

The database can also be used programmatically:

```python
from src.database import get_db_manager_from_env

# Initialize database manager
db = get_db_manager_from_env()

# Test connection
if db.test_connection():
    print("Database connected successfully!")

# Log an image
image_id = db.log_image_upload("board.jpg", "/path/to/board.jpg", "jpg")

# Start a job
job_id = db.start_job(image_id, "yolov8n.pt")

# Log a detection
detection_id = db.log_detection(job_id, "IC", 0.95, [100, 100, 200, 200])

# Log cropped IC
cropped_id = db.log_cropped_ic(job_id, detection_id, "/path/to/cropped_IC_0.jpg")

# Log OCR result
ocr_id = db.log_ocr_result(job_id, cropped_id, "LM358N", "LM358N", 0, 87.5)

# End job
db.end_job(job_id)

# Get job statistics
stats = db.get_job_statistics(job_id)
print(stats)
```

## Security Notes

⚠️ **Important**: The default credentials (`nuts_user`/`nuts_password`) are for development only. 

For production:
1. Change the password in `docker-compose.yml`
2. Use strong passwords
3. Consider using Docker secrets or environment variables
4. Restrict network access to the database
5. Enable SSL/TLS connections
6. Regular backups

## Performance Optimization

For better performance with large datasets:

```sql
-- Analyze tables for query optimization
ANALYZE images_input;
ANALYZE log_jobs;
ANALYZE detections;
ANALYZE ics_cropped;
ANALYZE ics_ocr;

-- Create additional indexes if needed
CREATE INDEX idx_detections_class_name ON detections(class_name);
CREATE INDEX idx_ics_ocr_cleaned_mpn ON ics_ocr(cleaned_mpn);
```
