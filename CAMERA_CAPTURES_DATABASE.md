# Camera Captures Database Feature

## Overview

The Camera Captures Database feature automatically logs all photos taken with the Arducam 108MP camera, preserving all camera settings and metadata for full traceability and reproducibility.

## Features

### Automatic Logging
- Every photo captured through the Camera Control page is automatically saved to the database
- All camera settings are preserved: focus, exposure, brightness, contrast, saturation
- Metadata includes: resolution, FPS, JPEG quality, file size, capture timestamp
- Works seamlessly whether using Preview Mode or Scan Mode

### Database Table: `camera_captures`

The `camera_captures` table stores:

| Field | Description |
|-------|-------------|
| `capture_id` | Unique identifier for each capture |
| `file_name` | Name of the saved image file |
| `file_path` | Full path to the image file |
| `captured_at` | Timestamp when the photo was taken |
| `camera_mode` | 'preview' or 'scan' mode |
| `resolution_width` | Image width in pixels |
| `resolution_height` | Image height in pixels |
| `fps` | Camera FPS setting at capture time |
| `focus_value` | Focus position (0-1023) |
| `exposure_value` | Exposure setting |
| `brightness` | Brightness value (0-255) |
| `contrast` | Contrast value (0-255) |
| `saturation` | Saturation value (0-255) |
| `jpeg_quality` | JPEG compression quality (0-100) |
| `file_size_bytes` | File size in bytes |
| `notes` | Optional notes (for future use) |

## Usage

### Capturing Photos with Database Logging

1. **Ensure Database is Connected**
   - Start PostgreSQL: `docker-compose up -d`
   - The web interface will show "✅ Database Connected" in the sidebar

2. **Capture Photos Normally**
   - Navigate to "📷 Camera Control" page
   - Choose your mode (Preview or Scan)
   - Connect camera and adjust settings
   - Click "📸 Capture Photo" or "📸 Capture High-Quality Scan"
   - The capture is automatically logged to the database

3. **Success Confirmation**
   - You'll see: "✅ Capture logged to database (ID: X)"
   - The photo is saved to disk AND logged to the database

### Viewing Capture History

#### Database Viewer Page
Navigate to "🗄️ Database Viewer" → Select "📷 Camera Captures"

**Features:**
- View all captures in a table format
- Filter by camera mode (All / Preview Mode / Scan Mode)
- See all camera settings for each capture
- Statistics: total captures, mode breakdown, file sizes
- Resolution distribution chart

#### Statistics Page
Navigate to "📊 Statistics" → Scroll to "📷 Camera Capture Statistics"

**Metrics shown:**
- Total captures count
- Preview mode captures
- Scan mode captures
- Average file size
- Last capture timestamp

## Benefits

### Traceability
- Complete history of all captures
- Know exactly what settings were used for each photo
- Track when photos were taken

### Reproducibility
- Can reproduce the exact same settings for a new capture
- Useful for A/B testing different settings
- Document optimal settings for different scenarios

### Analysis
- Compare file sizes across different resolutions
- Track usage patterns (Preview vs Scan mode)
- Monitor storage usage

### Quality Assurance
- Verify that high-quality scans were actually taken at the correct resolution
- Ensure focus and exposure settings were optimal
- Historical record for troubleshooting

## Two-Mode System Integration

The database seamlessly integrates with the two-mode camera system:

### Preview Mode (720p@60fps)
- Captures are logged with `camera_mode = 'preview'`
- Typically smaller file sizes (~0.5-1 MB)
- Used for settings adjustment and quick captures

### Scan Mode (4K/Ultra HQ)
- Captures are logged with `camera_mode = 'scan'`
- Larger file sizes (~3-10 MB depending on quality)
- Used for final high-quality captures for analysis

## Example Queries

### Get all scan mode captures
```python
captures = db.get_all_camera_captures(camera_mode='scan')
```

### Get capture statistics
```python
stats = db.get_camera_capture_statistics()
print(f"Total captures: {stats['total_captures']}")
print(f"Preview mode: {stats['preview_captures']}")
print(f"Scan mode: {stats['scan_captures']}")
```

### Get recent captures
```python
recent = db.get_all_camera_captures(limit=10)
for capture in recent:
    print(f"{capture['captured_at']}: {capture['file_name']} - {capture['camera_mode']} mode")
```

## Database Schema

```sql
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

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_camera_captures_captured_at ON camera_captures(captured_at);
CREATE INDEX IF NOT EXISTS idx_camera_captures_mode ON camera_captures(camera_mode);
```

## Optional: Database Not Connected

If the database is not connected:
- Photos are still saved to disk normally
- No error is shown (graceful fallback)
- A warning is logged in the application logs
- Database logging is simply skipped

This ensures the camera functionality works independently of the database.

## Troubleshooting

### Database not logging captures
1. Check database connection status in sidebar
2. Verify PostgreSQL is running: `docker-compose ps`
3. Check database logs: `docker-compose logs db`
4. Restart database: `docker-compose restart db`

### Cannot see captures in Database Viewer
1. Ensure at least one photo has been captured after database was connected
2. Click the "🔄 Refresh" button
3. Check the camera_captures table exists: Connect to database and run `\dt camera_captures`

### Disk space concerns
- Monitor total storage in Statistics page
- Consider periodic cleanup of old preview mode captures
- Scan mode captures should be preserved as they're the high-quality finals

## Future Enhancements

Potential features for future development:
- Add notes to captures via UI
- Bulk delete old preview captures
- Export capture settings as presets
- Link captures to detection jobs
- Automatic tagging based on content
- Search and filter by settings ranges

---

**Version:** 1.0  
**Date:** 2026-02-17  
**Camera:** Arducam 108MP USB 3.0 (B0494C)  
**Database:** PostgreSQL 15
