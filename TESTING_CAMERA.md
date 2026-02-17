# Testing Instructions for Arducam 108MP Integration

## Automated Tests (Already Completed)

✅ **Syntax Validation**: All Python files compile without errors
✅ **Code Review**: Passed with all comments addressed
✅ **Security Scan (CodeQL)**: No vulnerabilities found
✅ **Import Structure**: Module structure validated

## Manual Testing Required (Hardware Dependent)

Since the Arducam 108MP camera hardware is not available in this environment, the following tests should be performed with the actual camera hardware:

### 1. Basic Camera Connection Test

```bash
python example_camera.py
```

**Expected Result:**
- Camera connects successfully
- Camera info is displayed
- Focus adjustments work (0, 50, 100, 150, 200, 255)
- Auto-focus scan completes
- Photo is captured and saved
- Camera disconnects cleanly

**Verify:**
- Check that photo exists in `outputs/camera_captures/`
- Verify photo is not corrupted (can be opened in image viewer)
- Check photo metadata (resolution, quality)

### 2. Web Interface Test

```bash
streamlit run app.py
```

**Steps:**
1. Navigate to "📷 Camera Control" page
2. Set camera index to 0 (or appropriate value)
3. Click "🔌 Connect"
4. Verify status changes to "✅ Connected"
5. Adjust focus slider - camera should respond
6. Click "🔍 Auto Focus Scan" - should find optimal focus
7. Click "📸 Capture Frame" - should display preview
8. Click "📸 Capture Photo" - should save photo
9. Verify photo appears in interface
10. Click "🔄 Process Image" - should process through pipeline
11. Click "🔄 Disconnect" - camera should disconnect

**Verify:**
- All UI controls work
- No errors in console
- Photos are saved correctly
- Processing works end-to-end

### 3. Pipeline Integration Test

```bash
# Make sure you have a trained model first
python example_camera_pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --num-photos 3 \
  --use-database
```

**Expected Result:**
- Camera connects
- Auto-focus runs
- 3 photos are captured
- Each photo is processed
- Component detections are shown
- OCR results are displayed
- Results are saved to database (if --use-database)

**Verify:**
- Check `outputs/camera_captures/` for 3 photos
- Check `outputs/results/` for detection results
- If database enabled, verify entries in database tables
- Review accuracy of detections

### 4. Focus Control Test

**Manual Focus:**
```python
from src.camera_control import ArducamCamera

camera = ArducamCamera(camera_index=0)
camera.connect(width=1920, height=1080)

# Test different focus values
for focus in [0, 50, 100, 150, 200, 255]:
    camera.set_focus(focus)
    current = camera.get_focus()
    print(f"Set: {focus}, Read: {current}")
    
camera.disconnect()
```

**Verify:**
- Focus values are set correctly
- Visual inspection shows focus changes
- get_focus() returns expected values

**Auto Focus:**
```python
camera = ArducamCamera(camera_index=0)
camera.connect(width=1920, height=1080)

best_focus, sharpness = camera.auto_focus_scan(start=0, end=255, step=10)
print(f"Best focus: {best_focus} (sharpness: {sharpness})")

camera.disconnect()
```

**Verify:**
- Scan completes without errors
- Best focus value is reasonable (not 0 or 255 typically)
- Sharpness score increases as focus improves

### 5. Different Resolutions Test

```python
from src.camera_control import ArducamCamera

resolutions = [
    (640, 480),
    (1280, 720),
    (1920, 1080),
    (2560, 1440),
]

camera = ArducamCamera(camera_index=0)

for width, height in resolutions:
    if camera.connect(width=width, height=height):
        print(f"Testing {width}x{height}")
        photo = camera.capture_photo()
        if photo:
            print(f"  ✅ Captured: {photo}")
        camera.disconnect()
```

**Verify:**
- All resolutions work (camera dependent)
- Photos are saved with correct dimensions
- Higher resolutions produce larger files

### 6. Error Handling Test

**Camera Not Connected:**
```python
camera = ArducamCamera(camera_index=99)  # Invalid index
success = camera.connect()
# Should return False with error message
```

**Operations Without Connection:**
```python
camera = ArducamCamera(camera_index=0)
# Without calling connect():
camera.set_focus(100)  # Should show error
camera.capture_photo()  # Should show error
```

**Verify:**
- Errors are handled gracefully
- Informative error messages are displayed
- No crashes or exceptions

### 7. Resource Management Test

```python
# Test context manager
with ArducamCamera(camera_index=0) as camera:
    camera.connect(width=1920, height=1080)
    camera.capture_photo()
    # Camera should auto-disconnect on exit

# Test multiple connect/disconnect cycles
camera = ArducamCamera(camera_index=0)
for i in range(5):
    camera.connect()
    camera.capture_photo()
    camera.disconnect()
```

**Verify:**
- No resource leaks
- Camera can be reconnected multiple times
- Context manager properly cleans up

### 8. Performance Test

```python
import time
from src.camera_control import ArducamCamera

camera = ArducamCamera(camera_index=0)
camera.connect(width=1920, height=1080)

# Time auto-focus
start = time.time()
camera.auto_focus_scan(start=0, end=255, step=20)
focus_time = time.time() - start
print(f"Auto-focus took: {focus_time:.2f}s")

# Time photo capture
start = time.time()
for i in range(10):
    camera.capture_photo()
capture_time = (time.time() - start) / 10
print(f"Average capture time: {capture_time:.2f}s")

camera.disconnect()
```

**Expected:**
- Auto-focus: 15-30 seconds (depends on step size)
- Photo capture: < 1 second per photo

## Troubleshooting Tests

If any tests fail, run these diagnostic tests:

### Camera Detection
```bash
# Linux
ls -l /dev/video*
v4l2-ctl --list-devices

# Python
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### Driver Issues
```bash
# Check for camera in system
lsusb | grep -i camera

# Check dmesg for USB issues
dmesg | grep -i usb | tail -20
```

### Permission Issues (Linux)
```bash
# Add user to video group
sudo usermod -a -G video $USER

# Logout and login again
```

## Success Criteria

All tests should:
- ✅ Complete without crashes
- ✅ Display appropriate success/error messages
- ✅ Save photos to correct locations
- ✅ Return expected data types
- ✅ Clean up resources properly
- ✅ Work consistently across multiple runs

## Known Limitations

1. **Camera Index**: May need to try different indices (0, 1, 2, etc.)
2. **Resolution Support**: Camera may not support all resolutions
3. **Focus Range**: Actual range may vary by camera (0-255 is typical)
4. **Auto-Focus Time**: Depends on step size (larger steps = faster but less precise)

## Reporting Issues

If you encounter any issues during testing:

1. Note the exact error message
2. Check the relevant documentation section
3. Try the troubleshooting steps
4. Report on GitHub Issues with:
   - Python version
   - OS and version
   - Camera model and firmware
   - Full error traceback
   - Steps to reproduce

## Next Steps After Testing

Once all tests pass:
1. Document any camera-specific findings
2. Adjust default parameters if needed
3. Add any camera-specific notes to documentation
4. Share example photos (if appropriate)
5. Consider creating camera profiles for common use cases
