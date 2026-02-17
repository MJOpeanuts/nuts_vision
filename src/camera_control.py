#!/usr/bin/env python3
"""
Arducam 108MP Camera Control Module

Provides functionality to:
- Connect to Arducam 108MP USB 3.0 camera
- Control motorized focus (range: 0-1023)
- Capture high-resolution photos

Camera Specifications (Arducam 108MP):
- Sensor: 1/1.52" CMOS
- Max Resolution: 12000x9000 (108MP)
- Field of View: 85°(D)
- Supported Frame Rates (USB 3.0):
  * 1280x720@60fps (HD - Smooth video)
  * 3840x2160@10fps (4K UHD)
  * 4000x3000@7fps (Ultra high quality)
  * 12000x9000@1fps (108MP - requires demo app)
- Focus Range: 0-1023 (motorized)
"""

import cv2
import time
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime


class ArducamCamera:
    """
    Controller for Arducam 108MP Motorized Focus USB 3.0 Camera
    Reference: B0494C
    """
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize camera controller
        
        Args:
            camera_index: Camera device index (default: 0)
        """
        self.camera_index = camera_index
        self.cap = None
        self.width = None
        self.height = None
        self.fps = None
        self.is_connected = False
        
    def connect(self, width: int = 1920, height: int = 1080, fps: int = 30) -> bool:
        """
        Connect to the Arducam camera
        
        Args:
            width: Frame width (default: 1920)
            height: Frame height (default: 1080)
            fps: Frames per second (default: 30)
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Open camera using OpenCV VideoCapture
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                print(f"Error: Could not open camera at index {self.camera_index}")
                return False
            
            # Set camera properties
            self.width = width
            self.height = height
            self.fps = fps
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            
            # Disable autofocus to enable manual focus control
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            
            self.is_connected = True
            print(f"Camera connected successfully at {width}x{height}@{fps}fps")
            
            # Give camera time to initialize
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"Error connecting to camera: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the camera"""
        if self.cap is not None:
            self.cap.release()
            self.is_connected = False
            print("Camera disconnected")
    
    def set_focus(self, focus_value: int) -> bool:
        """
        Set the motorized focus
        
        Args:
            focus_value: Focus value (0-1023 for Arducam 108MP)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            print("Error: Camera not connected")
            return False
        
        try:
            # Set focus using OpenCV property
            self.cap.set(cv2.CAP_PROP_FOCUS, focus_value)
            
            # Give motor time to adjust
            time.sleep(0.3)
            
            print(f"Focus set to {focus_value}")
            return True
            
        except Exception as e:
            print(f"Error setting focus: {e}")
            return False
    
    def get_focus(self) -> Optional[int]:
        """
        Get current focus value
        
        Returns:
            Current focus value or None if error
        """
        if not self.is_connected:
            print("Error: Camera not connected")
            return None
        
        try:
            focus_value = self.cap.get(cv2.CAP_PROP_FOCUS)
            return int(focus_value)
        except Exception as e:
            print(f"Error getting focus: {e}")
            return None
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the camera
        
        Returns:
            Captured frame as numpy array or None if error
        """
        if not self.is_connected:
            print("Error: Camera not connected")
            return None
        
        try:
            ret, frame = self.cap.read()
            
            if not ret:
                print("Error: Failed to capture frame")
                return None
            
            return frame
            
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None
    
    def capture_photo(self, output_path: Optional[str] = None, quality: int = 95) -> Optional[str]:
        """
        Capture a high-resolution photo and save to disk
        
        Args:
            output_path: Path to save the photo (default: auto-generated timestamp)
            quality: JPEG quality (0-100, default: 95)
            
        Returns:
            Path to saved photo or None if error
        """
        if not self.is_connected:
            print("Error: Camera not connected")
            return None
        
        try:
            # Capture frame
            frame = self.capture_frame()
            
            if frame is None:
                return None
            
            # Generate output path if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path("outputs/camera_captures")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / f"arducam_{timestamp}.jpg")
            
            # Save image with high quality
            cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            
            print(f"Photo saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error capturing photo: {e}")
            return None
    
    def get_camera_info(self) -> dict:
        """
        Get camera information and current settings
        
        Returns:
            Dictionary with camera information
        """
        if not self.is_connected:
            return {"connected": False}
        
        info = {
            "connected": True,
            "index": self.camera_index,
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": int(self.cap.get(cv2.CAP_PROP_FPS)),
            "focus": self.get_focus(),
            "brightness": int(self.cap.get(cv2.CAP_PROP_BRIGHTNESS)),
            "contrast": int(self.cap.get(cv2.CAP_PROP_CONTRAST)),
            "saturation": int(self.cap.get(cv2.CAP_PROP_SATURATION)),
        }
        
        return info
    
    def auto_focus_scan(self, start: int = 0, end: int = 1023, step: int = 50) -> Tuple[int, float]:
        """
        Scan focus range to find optimal focus point using sharpness metric
        
        Args:
            start: Start focus value (default: 0)
            end: End focus value (default: 1023 for Arducam 108MP)
            step: Step size (default: 50)
            
        Returns:
            Tuple of (best_focus_value, best_sharpness_score)
        """
        if not self.is_connected:
            print("Error: Camera not connected")
            return (0, 0.0)
        
        print("Starting auto-focus scan...")
        best_focus = start
        best_sharpness = 0.0
        
        for focus_val in range(start, end + 1, step):
            self.set_focus(focus_val)
            time.sleep(0.5)  # Wait for focus to stabilize
            
            frame = self.capture_frame()
            if frame is not None:
                # Calculate sharpness using Laplacian variance
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                print(f"Focus {focus_val}: Sharpness {sharpness:.2f}")
                
                if sharpness > best_sharpness:
                    best_sharpness = sharpness
                    best_focus = focus_val
        
        # Set to best focus
        self.set_focus(best_focus)
        print(f"Auto-focus complete. Best focus: {best_focus} (sharpness: {best_sharpness:.2f})")
        
        return (best_focus, best_sharpness)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def main():
    """Example usage of ArducamCamera"""
    
    print("Arducam 108MP Camera Control Demo")
    print("=" * 50)
    
    # Create camera instance
    camera = ArducamCamera(camera_index=0)
    
    # Connect to camera with Arducam 108MP recommended settings
    if not camera.connect(width=1280, height=720, fps=60):
        print("Failed to connect to camera")
        return
    
    # Display camera info
    info = camera.get_camera_info()
    print("\nCamera Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test focus control with 0-1023 range
    print("\nTesting focus control...")
    for focus in [0, 200, 400, 600, 800, 1023]:
        camera.set_focus(focus)
        time.sleep(1)
    
    # Auto-focus scan with 0-1023 range
    print("\nPerforming auto-focus scan...")
    best_focus, sharpness = camera.auto_focus_scan(start=0, end=1023, step=50)
    
    # Capture a photo
    print("\nCapturing photo...")
    photo_path = camera.capture_photo()
    
    if photo_path:
        print(f"Photo captured successfully: {photo_path}")
    
    # Disconnect
    camera.disconnect()
    
    print("\nDemo complete!")


if __name__ == "__main__":
    main()
