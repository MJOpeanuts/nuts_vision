#!/usr/bin/env python3
"""
Example: Basic Arducam Camera Usage
Demonstrates how to connect, focus, and capture photos with the Arducam 108MP camera.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from camera_control import ArducamCamera


def main():
    """Example workflow for camera usage"""
    
    print("=" * 60)
    print("Arducam 108MP Camera - Basic Example")
    print("=" * 60)
    
    # Initialize camera
    print("\n1. Initializing camera...")
    camera = ArducamCamera(camera_index=0)
    
    # Connect to camera
    print("2. Connecting to camera...")
    if not camera.connect(width=1920, height=1080, fps=30):
        print("❌ Failed to connect to camera!")
        print("Make sure:")
        print("  - Camera is plugged into USB 3.0 port")
        print("  - Camera drivers are installed")
        print("  - Camera index is correct (try 0, 1, 2...)")
        return 1
    
    print("✅ Camera connected successfully!")
    
    # Display camera info
    print("\n3. Camera Information:")
    info = camera.get_camera_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Manual focus control
    print("\n4. Testing manual focus...")
    focus_values = [0, 50, 100, 150, 200, 255]
    for focus in focus_values:
        print(f"   Setting focus to {focus}...")
        camera.set_focus(focus)
        import time
        time.sleep(0.5)
    
    # Auto-focus
    print("\n5. Running auto-focus scan...")
    print("   This will scan through focus values to find optimal sharpness...")
    best_focus, sharpness = camera.auto_focus_scan(start=0, end=255, step=20)
    print(f"   ✅ Best focus: {best_focus} (sharpness score: {sharpness:.2f})")
    
    # Capture photo
    print("\n6. Capturing photo...")
    photo_path = camera.capture_photo(quality=95)
    
    if photo_path:
        print(f"   ✅ Photo saved: {photo_path}")
    else:
        print("   ❌ Failed to capture photo")
    
    # Disconnect
    print("\n7. Disconnecting camera...")
    camera.disconnect()
    print("   ✅ Camera disconnected")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
