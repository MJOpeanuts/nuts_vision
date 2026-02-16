#!/usr/bin/env python3
"""
Example/Demo Script for nuts_vision
Demonstrates the usage of the component detection and OCR pipeline.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from detect import ComponentDetector
from crop import ComponentCropper
from ocr import ComponentOCR
from visualize import DetectionVisualizer


def example_detection_only():
    """Example: Detection only without OCR."""
    print("="*60)
    print("EXAMPLE 1: Component Detection Only")
    print("="*60)
    
    # Check if model exists
    model_path = "models/best.pt"
    if not Path(model_path).exists():
        print(f"\nError: Model not found at {model_path}")
        print("Please train a model first:")
        print("  python src/train.py --data data.yaml --epochs 100")
        return
    
    # Initialize detector
    detector = ComponentDetector(model_path, conf_threshold=0.3)
    
    # Detect components
    print("\nDetecting components...")
    detections = detector.detect_components(
        "path/to/your/board_image.jpg",
        save_visualization=True,
        output_dir="outputs/results"
    )
    
    # Print results
    print(f"\nDetected {len(detections)} components:")
    for i, det in enumerate(detections, 1):
        print(f"  {i}. {det['class_name']}: confidence={det['confidence']:.2f}")


def example_full_pipeline():
    """Example: Full pipeline with detection, cropping, and OCR."""
    print("="*60)
    print("EXAMPLE 2: Full Pipeline (Detection + Cropping + OCR)")
    print("="*60)
    
    model_path = "models/best.pt"
    image_path = "path/to/your/board_image.jpg"
    
    # Check requirements
    if not Path(model_path).exists():
        print(f"\nError: Model not found at {model_path}")
        return
    
    if not Path(image_path).exists():
        print(f"\nError: Image not found at {image_path}")
        return
    
    # Step 1: Detection
    print("\n[1/4] Detecting components...")
    detector = ComponentDetector(model_path)
    detections = detector.detect_components(
        image_path,
        output_dir="outputs/results"
    )
    print(f"  Found {len(detections)} components")
    
    # Step 2: Cropping
    print("\n[2/4] Cropping components...")
    cropper = ComponentCropper(padding=10)
    cropped_paths = cropper.crop_from_detections(
        image_path,
        detections,
        output_dir="outputs/cropped_components"
    )
    print(f"  Saved {len(cropped_paths)} cropped images")
    
    # Step 3: OCR (only for ICs)
    print("\n[3/4] Extracting MPNs from ICs...")
    ocr = ComponentOCR()
    df = ocr.process_directory(
        "outputs/cropped_components",
        output_csv="outputs/results/mpn_results.csv",
        component_filter=['IC']
    )
    
    if not df.empty:
        successful = df[df['mpn'].notna() & (df['mpn'] != '')].shape[0]
        print(f"  Extracted {successful}/{len(df)} MPNs")
    
    # Step 4: Visualization
    print("\n[4/4] Creating visualizations...")
    viz = DetectionVisualizer("outputs/visualizations")
    viz.plot_detection_statistics("outputs/results/detections.json")
    if not df.empty:
        viz.plot_ocr_results("outputs/results/mpn_results.csv")
    print("  Visualizations saved")
    
    print("\n" + "="*60)
    print("Pipeline complete! Check the outputs/ directory")
    print("="*60)


def example_batch_processing():
    """Example: Process multiple images."""
    print("="*60)
    print("EXAMPLE 3: Batch Processing Multiple Images")
    print("="*60)
    
    model_path = "models/best.pt"
    image_dir = "path/to/your/images/"
    
    # Check requirements
    if not Path(model_path).exists():
        print(f"\nError: Model not found at {model_path}")
        return
    
    if not Path(image_dir).exists():
        print(f"\nError: Directory not found at {image_dir}")
        return
    
    # Process all images
    print("\nProcessing all images in directory...")
    detector = ComponentDetector(model_path)
    all_detections = detector.batch_detect(
        image_dir,
        output_dir="outputs/results"
    )
    
    # Summary
    total = sum(len(dets) for dets in all_detections.values())
    print(f"\nProcessed {len(all_detections)} images")
    print(f"Total components detected: {total}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("nuts_vision - Component Detection & OCR Examples")
    print("="*60)
    print("\nThis script demonstrates the usage of nuts_vision.")
    print("\nIMPORTANT: Update the image paths in this script before running!")
    print("\nAvailable examples:")
    print("  1. Detection only")
    print("  2. Full pipeline (detection + cropping + OCR)")
    print("  3. Batch processing")
    print("\nTo run an example, edit this file and uncomment the desired function.")
    print("="*60 + "\n")
    
    # Uncomment the example you want to run:
    
    # example_detection_only()
    # example_full_pipeline()
    # example_batch_processing()
    
    print("\nTo get started:")
    print("\n1. Train a model:")
    print("   python src/train.py --data data.yaml --epochs 100")
    print("\n2. Run the pipeline on your images:")
    print("   python src/pipeline.py --model runs/detect/component_detector/weights/best.pt --image your_image.jpg")
    print()


if __name__ == "__main__":
    main()
