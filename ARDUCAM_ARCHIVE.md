# ARDUCAM 108MP CAMERA — ARCHIVE

> **Note:** This file archives everything learned and implemented regarding the Arducam 108MP
> motorized focus USB 3.0 camera. This feature has been removed from nuts_vision to simplify
> the application and focus it on its core task: PCB image analysis from uploaded photos.

---

## Camera Used

**Arducam 108MP Motorized Focus USB 3.0 Camera** (model B0494C)

### Specifications
- Sensor: 1/1.52" CMOS
- Maximum Resolution: 12000×9000 (108 MP)
- Field of View: 85° (diagonal)
- Supported resolutions over USB 3.0:
  - 1280×720 @ 60 fps (HD — smooth video / preview)
  - 3840×2160 @ 10 fps (4K UHD)
  - 4000×3000 @ 7 fps (Ultra High Quality)
  - 12000×9000 @ 1 fps (108 MP — requires the Arducam demo app)
- Motorized focus range: 0–1023

---

## Driver & Software Setup (Linux / Raspberry Pi)

```bash
# Install Arducam UVC Control library
sudo apt install libopencv-dev
sudo pip install pyusb

# Arducam Python SDK for UVC control
git clone https://github.com/ArduCAM/ArduCAM_USB_Camera_Shield.git
cd ArduCAM_USB_Camera_Shield
python setup.py install

# Arducam Focus Control via V4L2
v4l2-ctl --device /dev/video0 --list-ctrls
# Focus is controlled via V4L2 property: focus_absolute (range 0-1023)
```

### Kernel modules required
```bash
lsmod | grep uvcvideo
# Should show: uvcvideo
```

### UVC focus control with Python (OpenCV)
```python
import cv2

cap = cv2.VideoCapture(0)
# V4L2 property for motorized focus
# CAP_PROP_FOCUS value mapped to 0-1 range (0 = near, 1 = far)
cap.set(cv2.CAP_PROP_FOCUS, focus_value / 1023.0)
```

---

## What Was Built

### `src/camera_control.py` — ArducamCamera class

A Python class providing:

- `connect(width, height, fps)` — opens OpenCV VideoCapture at specified resolution
- `disconnect()` — releases the capture
- `capture_frame()` — returns a single BGR frame
- `capture_photo(output_path, quality)` — saves a JPEG capture
- `set_focus(value)` / `get_focus()` — sets/reads V4L2 motorized focus (0–1023)
- `set_auto_exposure(enable)` — toggles auto exposure
- `set_exposure(value)` / `get_exposure()` — manual exposure control
- `set_gain(value)` / `get_gain()` — manual gain/ISO control
- `set_brightness(value)` / `set_contrast(value)` / `set_saturation(value)` — image quality parameters
- `auto_focus_scan(start, end, step)` — sweeps focus values, measures Laplacian sharpness, returns best value
- `get_camera_info()` — returns dict with current resolution, fps, focus, exposure, etc.

### Two-Mode Workflow in `app.py`

The web interface implemented two camera operating modes:

1. **Preview Mode** (1280×720 @ 60 fps)
   - Fast, smooth live preview
   - Used to adjust focus, exposure, brightness, contrast, saturation in real time
   - Streamlit `st.rerun()` loop for continuous frame display
   - Sharpness indicator (Laplacian variance) shown in caption

2. **Scan Mode** (3840×2160 @ 10 fps or 4000×3000 @ 7 fps)
   - High-resolution single-frame capture
   - Switched to after settings are tuned in Preview Mode
   - Captured photo saved to `captures/` directory

### Auto-Focus Algorithm

```python
def auto_focus_scan(self, start=0, end=1023, step=50):
    best_focus = start
    best_sharpness = 0
    for focus_val in range(start, end + 1, step):
        self.set_focus(focus_val)
        time.sleep(0.2)  # let lens settle
        frame = self.capture_frame()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        if sharpness > best_sharpness:
            best_sharpness = sharpness
            best_focus = focus_val
    self.set_focus(best_focus)
    return best_focus, best_sharpness
```

---

## Database Table: `camera_captures`

A dedicated PostgreSQL table was used to log every capture:

```sql
CREATE TABLE camera_captures (
    capture_id        SERIAL PRIMARY KEY,
    file_name         VARCHAR(255) NOT NULL,
    file_path         TEXT NOT NULL,
    captured_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    camera_mode       VARCHAR(20) CHECK (camera_mode IN ('preview', 'scan')),
    resolution_width  INTEGER,
    resolution_height INTEGER,
    fps               INTEGER,
    focus_value       INTEGER,
    exposure_value    INTEGER,
    brightness        INTEGER,
    contrast          INTEGER,
    saturation        INTEGER,
    jpeg_quality      INTEGER,
    file_size_bytes   BIGINT,
    notes             TEXT
);
```

Each photo captured through the Streamlit UI was logged with full camera settings.

---

## Known Issues / Lessons Learned

- **Focus on Raspberry Pi 4**: On some systems, `cv2.CAP_PROP_FOCUS` is read-only; the
  V4L2 UVC control must be set directly via `v4l2-ctl` or the Arducam SDK.
- **High resolution startup latency**: At 4K and above, the first few frames may be
  black or noisy — discard at least 5 warm-up frames before capturing.
- **USB bandwidth**: 108 MP mode requires USB 3.0 (blue port). A USB 2.0 port will fail
  or fall back silently to a lower resolution.
- **Frame timing at 60 fps**: Streamlit's `st.rerun()` loop adds inherent latency
  (network round-trip + render). Actual displayed frame rate is closer to 10–15 fps in
  the browser, even if the camera outputs 60 fps.
- **OpenCV backend on Raspberry Pi**: Use `cv2.VideoCapture(index, cv2.CAP_V4L2)` to
  force V4L2 backend; the default FFMPEG backend may not expose all V4L2 controls.

---

## Files Removed (previously in repository)

| File | Description |
|------|-------------|
| `src/camera_control.py` | ArducamCamera Python class |
| `example_camera.py` | Standalone usage example |
| `example_camera_pipeline.py` | Camera + pipeline integration example |
| `test_camera_controls.py` | Unit tests for camera controls |
| `ARDUCAM_108MP_CONFIG.md` | Hardware configuration guide |
| `ARDUCAM_OPTIMIZATION.md` | Performance optimisation notes |
| `ARDUCAM_UPDATE_SUMMARY.md` | Changelog for camera feature |
| `CAMERA.md` | General camera documentation |
| `CAMERA_CAPTURES_DATABASE.md` | Database logging for captures |
| `CAMERA_GUIDE_FR.md` | French camera guide |
| `DIAGNOSTIC_ARDUCAM.md` | Troubleshooting guide |
| `IMPLEMENTATION_CAMERA.md` | Camera implementation details |
| `IMPLEMENTATION_CAMERA_CAPTURES.md` | Capture implementation details |
| `LIVE_PREVIEW_FEATURE.md` | Live preview implementation |
| `TESTING_CAMERA.md` | Camera testing guide |
| `SUMMARY_TWO_MODES.md` | Two-mode workflow summary |
| `WORKFLOW_TWO_MODES.md` | Two-mode workflow details |

---

*Archived on removal of camera features from nuts_vision (v2.0 simplification).*
