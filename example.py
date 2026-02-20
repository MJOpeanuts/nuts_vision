#!/usr/bin/env python3
"""
Example/Demo Script for nuts_vision
Demonstrates the usage of the IC detection pipeline.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from detect import ComponentDetector
from pipeline import ComponentAnalysisPipeline


def example_detection_only():
    """Example: Detection only."""
    print("="*60)
    print("EXAMPLE 1: IC Detection Only")
    print("="*60)

    model_path = "best.pt"
    if not Path(model_path).exists():
        print(f"\nError: Model not found at {model_path}")
        print("Please place best.pt in the project root directory.")
        return

    detector = ComponentDetector(model_path, conf_threshold=0.3)

    print("\nDetecting ICs...")
    detections = detector.detect_components(
        "path/to/your/board_image.jpg",
        save_visualization=True,
        output_dir="outputs/results"
    )

    print(f"\nDetected {len(detections)} ICs:")
    for i, det in enumerate(detections, 1):
        print(f"  {i}. {det['class_name']}: confidence={det['confidence']:.2f}")


def example_pipeline():
    """Example: Detection + cropping via pipeline."""
    print("="*60)
    print("EXAMPLE 2: Full Pipeline (Detection + Cropping)")
    print("="*60)

    model_path = "best.pt"
    image_path = "path/to/your/board_image.jpg"

    if not Path(model_path).exists():
        print(f"\nError: Model not found at {model_path}")
        return

    if not Path(image_path).exists():
        print(f"\nError: Image not found at {image_path}")
        return

    pipeline = ComponentAnalysisPipeline(model_path)
    result = pipeline.process_image(image_path, jobs_base_dir="jobs")

    print(f"\nJob folder: {result['job_folder']}")
    print(f"Total detections: {result['metadata']['total_detections']}")
    print(f"Crops saved: {len(result['crop_photos'])}")


def example_batch_processing():
    """Example: Process multiple images."""
    print("="*60)
    print("EXAMPLE 3: Batch Processing Multiple Images")
    print("="*60)

    model_path = "best.pt"
    image_dir = "path/to/your/images/"

    if not Path(model_path).exists():
        print(f"\nError: Model not found at {model_path}")
        return

    if not Path(image_dir).exists():
        print(f"\nError: Directory not found at {image_dir}")
        return

    detector = ComponentDetector(model_path)
    all_detections = detector.batch_detect(image_dir, output_dir="outputs/results")

    total = sum(len(dets) for dets in all_detections.values())
    print(f"\nProcessed {len(all_detections)} images")
    print(f"Total ICs detected: {total}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("nuts_vision - IC Detection Examples")
    print("="*60)
    print("\nThis script demonstrates the usage of nuts_vision.")
    print("\nIMPORTANT: Update the image paths in this script before running!")
    print("\nAvailable examples:")
    print("  1. Detection only")
    print("  2. Full pipeline (detection + cropping, per-job folder)")
    print("  3. Batch processing")
    print("\nTo run an example, edit this file and uncomment the desired function.")
    print("="*60 + "\n")

    # Uncomment the example you want to run:

    # example_detection_only()
    # example_pipeline()
    # example_batch_processing()

    print("\nTo get started:")
    print("\n1. Run the pipeline on your images:")
    print("   python src/pipeline.py --model best.pt --image your_image.jpg")
    print()


if __name__ == "__main__":
    main()
