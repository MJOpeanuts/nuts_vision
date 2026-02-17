-- Database schema for nuts_vision
-- Traces all image processing and extraction operations

-- Table: images_input
-- Stores information about uploaded images
CREATE TABLE IF NOT EXISTS images_input (
    image_id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    upload_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    format VARCHAR(10)
);

-- Table: log_jobs
-- Logs detection jobs and their execution details
CREATE TABLE IF NOT EXISTS log_jobs (
    job_id SERIAL PRIMARY KEY,
    image_id INTEGER NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    model VARCHAR(255),
    FOREIGN KEY (image_id) REFERENCES images_input(image_id) ON DELETE CASCADE
);

-- Table: detections
-- Stores detection results for each job
CREATE TABLE IF NOT EXISTS detections (
    detection_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    bbox_x1 FLOAT NOT NULL,
    bbox_y1 FLOAT NOT NULL,
    bbox_x2 FLOAT NOT NULL,
    bbox_y2 FLOAT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES log_jobs(job_id) ON DELETE CASCADE
);

-- Table: ics_cropped
-- Links jobs to cropped IC images
CREATE TABLE IF NOT EXISTS ics_cropped (
    cropped_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL,
    detection_id INTEGER NOT NULL,
    cropped_file_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES log_jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (detection_id) REFERENCES detections(detection_id) ON DELETE CASCADE
);

-- Table: ics_ocr
-- Stores OCR results for cropped IC images
CREATE TABLE IF NOT EXISTS ics_ocr (
    ocr_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL,
    cropped_id INTEGER NOT NULL,
    raw_text TEXT,
    cleaned_mpn VARCHAR(255),
    rotation_angle INTEGER CHECK (rotation_angle IN (0, 90, 180, 270)),
    confidence FLOAT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES log_jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (cropped_id) REFERENCES ics_cropped(cropped_id) ON DELETE CASCADE
);

-- Table: camera_captures
-- Stores camera captures with camera settings and metadata
CREATE TABLE IF NOT EXISTS camera_captures (
    capture_id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    camera_mode VARCHAR(20) CHECK (camera_mode IN ('preview', 'scan')),
    resolution_width INTEGER,
    resolution_height INTEGER,
    fps INTEGER,
    focus_value INTEGER,
    exposure_value INTEGER,
    brightness INTEGER,
    contrast INTEGER,
    saturation INTEGER,
    jpeg_quality INTEGER,
    file_size_bytes BIGINT,
    notes TEXT
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_log_jobs_image_id ON log_jobs(image_id);
CREATE INDEX IF NOT EXISTS idx_detections_job_id ON detections(job_id);
CREATE INDEX IF NOT EXISTS idx_ics_cropped_job_id ON ics_cropped(job_id);
CREATE INDEX IF NOT EXISTS idx_ics_cropped_detection_id ON ics_cropped(detection_id);
CREATE INDEX IF NOT EXISTS idx_ics_ocr_job_id ON ics_ocr(job_id);
CREATE INDEX IF NOT EXISTS idx_ics_ocr_cropped_id ON ics_ocr(cropped_id);
CREATE INDEX IF NOT EXISTS idx_camera_captures_captured_at ON camera_captures(captured_at);
CREATE INDEX IF NOT EXISTS idx_camera_captures_mode ON camera_captures(camera_mode);
