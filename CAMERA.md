# Arducam 108MP Camera Integration

This document describes how to use the Arducam 108MP Motorized Focus USB 3.0 Camera with nuts_vision.

## Camera Specifications

- **Model**: Arducam 108MP Motorized Focus USB 3.0 Camera
- **Reference**: B0494C
- **Link**: [Arducam 108MP Product Page](https://www.arducam.com/arducam-108mp-motorized-focus-usb-3-0-camera-module.html)

## Features

The camera integration provides:

1. **Camera Connection**: Connect to the Arducam 108MP camera via USB 3.0
2. **Focus Control**: Adjust the motorized focus manually or automatically
3. **Photo Capture**: Capture high-resolution photos
4. **Pipeline Integration**: Process captured photos through the component detection pipeline

## Installation

### Prerequisites

1. **Hardware**: Arducam 108MP camera connected via USB 3.0
2. **Software**: All dependencies are included in `requirements.txt`

### Verify Installation

Check that OpenCV can access the camera:

```bash
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

If this returns `True`, the camera is accessible.

## Usage

### Method 1: Web Interface (Recommended)

The easiest way to use the camera is through the Streamlit web interface:

```bash
# Start the web interface
streamlit run app.py
```

Then navigate to the **📷 Camera Control** page in the sidebar.

**Steps:**
1. **Connect**: Enter camera index (usually 0) and click "Connect"
2. **Adjust Focus**: 
   - Use the slider for manual focus control
   - Click "Auto Focus Scan" for automatic focus optimization
3. **Capture**: Click "Capture Photo" to take a high-resolution image
4. **Process**: Click "Process Image" to run component detection on the captured photo

### Method 2: Python API

You can also use the camera programmatically:

```python
from src.camera_control import ArducamCamera

# Create camera instance
camera = ArducamCamera(camera_index=0)

# Connect to camera
if camera.connect(width=1920, height=1080, fps=30):
    print("Camera connected!")
    
    # Set focus manually
    camera.set_focus(150)
    
    # Or perform auto-focus
    best_focus, sharpness = camera.auto_focus_scan()
    print(f"Optimal focus: {best_focus}")
    
    # Capture a photo
    photo_path = camera.capture_photo(quality=95)
    print(f"Photo saved: {photo_path}")
    
    # Disconnect
    camera.disconnect()
```

### Method 3: Context Manager

For cleaner code, use the context manager:

```python
from src.camera_control import ArducamCamera

with ArducamCamera(camera_index=0) as camera:
    if camera.connect(width=1920, height=1080):
        # Auto-focus
        camera.auto_focus_scan()
        
        # Capture photo
        photo_path = camera.capture_photo()
        
        # Camera automatically disconnects
```

## Integration with Pipeline

To capture and process images in one workflow:

```python
from src.camera_control import ArducamCamera
from src.pipeline import ComponentAnalysisPipeline

# Initialize camera and pipeline
camera = ArducamCamera(camera_index=0)
pipeline = ComponentAnalysisPipeline(
    model_path="runs/detect/component_detector/weights/best.pt",
    use_database=True
)

# Connect and capture
if camera.connect(width=1920, height=1080):
    # Auto-focus for best results
    camera.auto_focus_scan()
    
    # Capture photo
    photo_path = camera.capture_photo()
    
    # Process through pipeline
    results = pipeline.process_image(photo_path)
    
    print(f"Detected {len(results.get('detections', []))} components")
    
    camera.disconnect()
```

## API Reference

### ArducamCamera Class

#### Constructor
```python
ArducamCamera(camera_index: int = 0)
```
- `camera_index`: Device index for the camera (default: 0)

#### Methods

**connect(width, height, fps)**
```python
connect(width: int = 1920, height: int = 1080, fps: int = 30) -> bool
```
Connect to the camera with specified resolution and frame rate.

**disconnect()**
```python
disconnect()
```
Disconnect from the camera and release resources.

**set_focus(focus_value)**
```python
set_focus(focus_value: int) -> bool
```
Set the motorized focus (0-255).

**get_focus()**
```python
get_focus() -> Optional[int]
```
Get the current focus value.

**capture_frame()**
```python
capture_frame() -> Optional[np.ndarray]
```
Capture a single frame from the camera.

**capture_photo(output_path, quality)**
```python
capture_photo(output_path: Optional[str] = None, quality: int = 95) -> Optional[str]
```
Capture and save a high-resolution photo.
- `output_path`: Custom save path (default: auto-generated with timestamp)
- `quality`: JPEG quality 0-100 (default: 95)

**auto_focus_scan(start, end, step)**
```python
auto_focus_scan(start: int = 0, end: int = 255, step: int = 10) -> Tuple[int, float]
```
Scan focus range to find optimal focus using sharpness metric.
- Returns: `(best_focus_value, best_sharpness_score)`

**get_camera_info()**
```python
get_camera_info() -> dict
```
Get camera information and current settings.

## Troubleshooting

### Camera Not Found

**Error**: "Could not open camera at index 0"

**Solutions**:
1. Verify camera is plugged into USB 3.0 port
2. Check camera power LED is on
3. Try different camera indices (0, 1, 2, etc.)
4. Check camera permissions (Linux: add user to `video` group)
5. Verify with: `ls /dev/video*` (Linux) or Device Manager (Windows)

### Focus Not Working

**Error**: Focus slider has no effect

**Solutions**:
1. Ensure camera supports motorized focus (Arducam 108MP does)
2. Check that autofocus is disabled in camera settings
3. Try larger focus steps (e.g., move from 0 to 100)
4. Some cameras need time to adjust - wait 0.5-1 second

### Poor Image Quality

**Solutions**:
1. Use auto-focus scan for optimal focus
2. Increase capture quality parameter (up to 100)
3. Use higher resolution (e.g., 1920x1080 or higher)
4. Ensure good lighting conditions
5. Clean camera lens

### Connection Drops

**Solutions**:
1. Use high-quality USB 3.0 cable
2. Connect directly to computer (not through hub)
3. Check USB power delivery
4. Update camera firmware if available

## Performance Tips

1. **Resolution**: Use 1920x1080 for fast preview, higher for final capture
2. **Auto-Focus**: Run once before multiple captures (doesn't need to be repeated)
3. **Quality**: Use 85-95 for good balance of quality and file size
4. **Lighting**: Ensure consistent, bright lighting for best detection results
5. **Distance**: Position camera 10-30cm from PCB for optimal results

## Camera Modes

### Preview Mode
- Lower resolution (e.g., 1280x720)
- Higher frame rate (30 fps)
- Good for focusing and positioning

### Capture Mode
- High resolution (e.g., 1920x1080 or higher)
- Lower frame rate (10-15 fps)
- Best quality for component detection

## Advanced Usage

### Multiple Cameras

If you have multiple cameras connected:

```python
# Camera 0
camera_0 = ArducamCamera(camera_index=0)

# Camera 1
camera_1 = ArducamCamera(camera_index=1)
```

### Custom Focus Algorithm

Implement your own focus optimization:

```python
def custom_focus_scan(camera):
    best_focus = 0
    best_score = 0
    
    for focus in range(0, 256, 5):
        camera.set_focus(focus)
        frame = camera.capture_frame()
        
        # Your custom sharpness metric
        score = calculate_sharpness(frame)
        
        if score > best_score:
            best_score = score
            best_focus = focus
    
    camera.set_focus(best_focus)
    return best_focus
```

## Examples

See the [examples](../examples/) directory for:
- `camera_basic.py`: Basic camera usage
- `camera_autofocus.py`: Auto-focus examples
- `camera_batch_capture.py`: Batch photo capture
- `camera_pipeline_integration.py`: Full pipeline integration

## Support

For issues specific to:
- **Camera hardware**: [Arducam Support](https://www.arducam.com/support/)
- **nuts_vision integration**: [GitHub Issues](https://github.com/MJOpeanuts/nuts_vision/issues)

## License

This integration is part of nuts_vision and is licensed under CC BY 4.0.
