#!/usr/bin/env python3
"""
Example: Camera + Pipeline Integration
Demonstrates capturing photos with Arducam and processing them through the detection pipeline.
"""

import sys
from pathlib import Path
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from camera_control import ArducamCamera
from pipeline import ComponentAnalysisPipeline


def main():
    """Example workflow: Capture and process"""
    
    parser = argparse.ArgumentParser(description="Capture and process PCB images")
    parser.add_argument("--model", type=str, 
                       default="runs/detect/component_detector/weights/best.pt",
                       help="Path to YOLO model")
    parser.add_argument("--camera-index", type=int, default=0,
                       help="Camera device index")
    parser.add_argument("--width", type=int, default=1920,
                       help="Capture width")
    parser.add_argument("--height", type=int, default=1080,
                       help="Capture height")
    parser.add_argument("--num-photos", type=int, default=1,
                       help="Number of photos to capture and process")
    parser.add_argument("--use-database", action="store_true",
                       help="Enable database logging")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Arducam 108MP Camera + Component Detection Pipeline")
    print("=" * 70)
    
    # Check if model exists
    if not Path(args.model).exists():
        print(f"\n❌ Model not found: {args.model}")
        print("Please train a model first using:")
        print("  python src/train.py --data data.yaml --epochs 100 --model-size n")
        return 1
    
    # Initialize camera
    print("\n[1/4] Connecting to camera...")
    camera = ArducamCamera(camera_index=args.camera_index)
    
    if not camera.connect(width=args.width, height=args.height, fps=30):
        print("❌ Failed to connect to camera!")
        return 1
    
    print("✅ Camera connected")
    
    # Auto-focus
    print("\n[2/4] Running auto-focus...")
    best_focus, sharpness = camera.auto_focus_scan(start=0, end=255, step=20)
    print(f"✅ Optimal focus: {best_focus} (sharpness: {sharpness:.2f})")
    
    # Initialize pipeline
    print("\n[3/4] Initializing detection pipeline...")
    try:
        pipeline = ComponentAnalysisPipeline(
            model_path=args.model,
            use_database=args.use_database
        )
        print("✅ Pipeline initialized")
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        camera.disconnect()
        return 1
    
    # Capture and process photos
    print(f"\n[4/4] Capturing and processing {args.num_photos} photo(s)...")
    
    for i in range(args.num_photos):
        print(f"\n  Photo {i+1}/{args.num_photos}:")
        
        # Capture
        print("    📷 Capturing...")
        photo_path = camera.capture_photo(quality=95)
        
        if not photo_path:
            print("    ❌ Failed to capture photo")
            continue
        
        print(f"    ✅ Captured: {photo_path}")
        
        # Process
        print("    🔄 Processing through pipeline...")
        try:
            results = pipeline.process_image(photo_path)
            
            num_detections = len(results.get('detections', []))
            num_ocr = len(results.get('ocr_results', []))
            
            print(f"    ✅ Detected {num_detections} components")
            print(f"    ✅ Extracted {num_ocr} MPNs via OCR")
            
            # Display some results
            if results.get('detections'):
                print("\n    Component breakdown:")
                component_counts = {}
                for det in results['detections']:
                    comp_type = det.get('class', 'Unknown')
                    component_counts[comp_type] = component_counts.get(comp_type, 0) + 1
                
                for comp_type, count in sorted(component_counts.items()):
                    print(f"      - {comp_type}: {count}")
            
            if results.get('ocr_results'):
                print("\n    Extracted MPNs:")
                for ocr_result in results['ocr_results'][:5]:  # Show first 5
                    mpn = ocr_result.get('mpn', 'N/A')
                    conf = ocr_result.get('confidence', 0)
                    print(f"      - {mpn} (confidence: {conf:.2f})")
                
                if len(results['ocr_results']) > 5:
                    print(f"      ... and {len(results['ocr_results']) - 5} more")
        
        except Exception as e:
            print(f"    ❌ Error processing image: {e}")
            import traceback
            traceback.print_exc()
        
        # Brief pause between photos
        if i < args.num_photos - 1:
            import time
            print("\n    Waiting 2 seconds before next capture...")
            time.sleep(2)
    
    # Cleanup
    print("\n[5/4] Cleaning up...")
    camera.disconnect()
    print("✅ Camera disconnected")
    
    print("\n" + "=" * 70)
    print("Workflow completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("  - Check outputs/camera_captures/ for captured images")
    print("  - Check outputs/results/ for detection results")
    if args.use_database:
        print("  - View results in database via web interface: streamlit run app.py")
    
    return 0


if __name__ == "__main__":
    exit(main())
