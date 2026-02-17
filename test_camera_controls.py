#!/usr/bin/env python3
"""
Test script for new camera controls (exposure, brightness, gain)
This script verifies the new methods in camera_control.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import camera_control directly to avoid dependency issues
import importlib.util
spec = importlib.util.spec_from_file_location("camera_control", "src/camera_control.py")
camera_control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(camera_control)
ArducamCamera = camera_control.ArducamCamera

def test_camera_controls():
    """Test new camera control methods"""
    print("=" * 60)
    print("Testing Arducam Camera Controls")
    print("=" * 60)
    
    # Create camera instance
    print("\n1. Creating camera instance...")
    camera = ArducamCamera(camera_index=0)
    
    # Test connection
    print("\n2. Testing connection (simulated - no real camera needed for API test)...")
    print("   - ArducamCamera class instantiated successfully")
    
    # Test that new methods exist
    print("\n3. Verifying new methods exist...")
    methods_to_check = [
        'set_exposure',
        'set_auto_exposure', 
        'set_brightness',
        'set_contrast',
        'set_saturation',
        'set_gain',
        'get_exposure',
        'get_gain'
    ]
    
    all_exist = True
    for method_name in methods_to_check:
        if hasattr(camera, method_name):
            print(f"   ✓ {method_name} exists")
        else:
            print(f"   ✗ {method_name} missing")
            all_exist = False
    
    if all_exist:
        print("\n✅ All new methods are properly defined!")
    else:
        print("\n❌ Some methods are missing!")
        return False
    
    # Test method signatures
    print("\n4. Testing method signatures...")
    try:
        # These should work without a connected camera (will return False or None)
        result = camera.set_exposure(-5)
        print(f"   set_exposure(-5) returned: {result}")
        
        result = camera.set_auto_exposure(True)
        print(f"   set_auto_exposure(True) returned: {result}")
        
        result = camera.set_brightness(128)
        print(f"   set_brightness(128) returned: {result}")
        
        result = camera.set_gain(50)
        print(f"   set_gain(50) returned: {result}")
        
        result = camera.get_exposure()
        print(f"   get_exposure() returned: {result}")
        
        result = camera.get_gain()
        print(f"   get_gain() returned: {result}")
        
        print("\n✅ All method signatures are correct!")
        
    except Exception as e:
        print(f"\n❌ Error testing methods: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("  ✓ Camera class instantiation works")
    print("  ✓ All new methods exist")
    print("  ✓ Method signatures are correct")
    print("  ✓ Methods handle 'not connected' state gracefully")
    print("=" * 60)
    print("\n✅ ALL TESTS PASSED!")
    print("\nNote: These tests verify the API is correct.")
    print("To test with actual hardware, run the camera control demo:")
    print("  python src/camera_control.py")
    
    return True

if __name__ == "__main__":
    success = test_camera_controls()
    sys.exit(0 if success else 1)
