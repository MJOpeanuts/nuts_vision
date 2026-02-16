#!/usr/bin/env python3
"""
Complete Pipeline for Electronic Component Detection and OCR
Combines detection, cropping, and OCR into a single workflow.
"""

import argparse
from pathlib import Path
import sys

# Import our modules
from detect import ComponentDetector
from crop import ComponentCropper
from ocr import ComponentOCR
from visualize import DetectionVisualizer


class ComponentAnalysisPipeline:
    """Complete pipeline for component detection and MPN extraction."""
    
    def __init__(
        self,
        model_path: str,
        conf_threshold: float = 0.25,
        padding: int = 10
    ):
        """
        Initialize the pipeline.
        
        Args:
            model_path: Path to trained YOLO model
            conf_threshold: Confidence threshold for detections
            padding: Padding for cropped components
        """
        self.detector = ComponentDetector(model_path, conf_threshold)
        self.cropper = ComponentCropper(padding)
        self.ocr = ComponentOCR()
        self.visualizer = DetectionVisualizer()
        
    def run_pipeline(
        self,
        image_path: str = None,
        image_dir: str = None,
        output_base_dir: str = "outputs",
        extract_mpn: bool = True,
        create_visualizations: bool = True
    ):
        """
        Run the complete analysis pipeline.
        
        Args:
            image_path: Path to single image (optional)
            image_dir: Directory of images (optional)
            output_base_dir: Base directory for outputs
            extract_mpn: Whether to run OCR for MPN extraction
            create_visualizations: Whether to create visualization plots
        """
        output_base = Path(output_base_dir)
        results_dir = output_base / "results"
        cropped_dir = output_base / "cropped_components"
        viz_dir = output_base / "visualizations"
        
        # Create directories
        for dir_path in [results_dir, cropped_dir, viz_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print("="*60)
        print("ELECTRONIC COMPONENT ANALYSIS PIPELINE")
        print("="*60)
        
        # Step 1: Detection
        print("\n[STEP 1/4] Running component detection...")
        print("-"*60)
        
        if image_path:
            detections = self.detector.detect_components(
                image_path,
                output_dir=str(results_dir)
            )
            detection_dict = {image_path: detections}
            print(f"Detected {len(detections)} components in image")
        elif image_dir:
            detection_dict = self.detector.batch_detect(
                image_dir,
                output_dir=str(results_dir)
            )
            total_detections = sum(len(dets) for dets in detection_dict.values())
            print(f"Detected {total_detections} total components across {len(detection_dict)} images")
        else:
            raise ValueError("Either image_path or image_dir must be provided")
        
        # Step 2: Cropping
        print("\n[STEP 2/4] Cropping detected components...")
        print("-"*60)
        
        all_cropped = {}
        for img_path, detections in detection_dict.items():
            if detections:
                cropped_paths = self.cropper.crop_from_detections(
                    img_path,
                    detections,
                    output_dir=str(cropped_dir)
                )
                all_cropped[img_path] = cropped_paths
                print(f"Cropped {len(cropped_paths)} components from {Path(img_path).name}")
        
        total_cropped = sum(len(paths) for paths in all_cropped.values())
        print(f"\nTotal cropped components: {total_cropped}")
        
        # Step 3: OCR (if requested)
        ocr_df = None
        if extract_mpn:
            print("\n[STEP 3/4] Extracting MPNs using OCR...")
            print("-"*60)
            
            ocr_df = self.ocr.process_directory(
                input_dir=str(cropped_dir),
                output_csv=str(results_dir / "mpn_results.csv"),
                output_json=str(results_dir / "mpn_results.json"),
                component_filter=['IC']  # Focus on ICs for MPN extraction
            )
            
            if not ocr_df.empty:
                successful_mpn = ocr_df[ocr_df['mpn'].notna() & (ocr_df['mpn'] != '')].shape[0]
                print(f"\nExtracted MPNs: {successful_mpn}/{len(ocr_df)}")
        else:
            print("\n[STEP 3/4] Skipping OCR (--no-ocr flag set)")
        
        # Step 4: Visualization (if requested)
        if create_visualizations:
            print("\n[STEP 4/4] Creating visualizations...")
            print("-"*60)
            
            # Detection statistics
            detection_file = results_dir / "detections.json"
            if detection_file.exists():
                self.visualizer.plot_detection_statistics(
                    str(detection_file),
                    save_path=str(viz_dir / "detection_statistics.png")
                )
            
            # OCR results
            if ocr_df is not None and not ocr_df.empty:
                ocr_csv = results_dir / "mpn_results.csv"
                if ocr_csv.exists():
                    self.visualizer.plot_ocr_results(
                        str(ocr_csv),
                        save_path=str(viz_dir / "ocr_results.png")
                    )
        else:
            print("\n[STEP 4/4] Skipping visualizations (--no-viz flag set)")
        
        # Summary
        print("\n" + "="*60)
        print("PIPELINE COMPLETE!")
        print("="*60)
        print(f"\nResults saved to: {output_base}")
        print(f"  - Detections: {results_dir}")
        print(f"  - Cropped components: {cropped_dir}")
        if extract_mpn:
            print(f"  - MPN extraction: {results_dir / 'mpn_results.csv'}")
        if create_visualizations:
            print(f"  - Visualizations: {viz_dir}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Complete pipeline for component detection and MPN extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single image
  python pipeline.py --model models/best.pt --image test_board.jpg
  
  # Process a directory of images
  python pipeline.py --model models/best.pt --image-dir images/
  
  # Process without OCR
  python pipeline.py --model models/best.pt --image-dir images/ --no-ocr
  
  # Process with custom confidence threshold
  python pipeline.py --model models/best.pt --image test.jpg --conf 0.5
        """
    )
    
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to trained YOLO model"
    )
    parser.add_argument(
        "--image",
        type=str,
        help="Path to single image to process"
    )
    parser.add_argument(
        "--image-dir",
        type=str,
        help="Directory of images to process"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Base directory for outputs (default: outputs)"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold for detections (default: 0.25)"
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=10,
        help="Padding around cropped components in pixels (default: 10)"
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Skip OCR/MPN extraction step"
    )
    parser.add_argument(
        "--no-viz",
        action="store_true",
        help="Skip visualization generation"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.image and not args.image_dir:
        parser.error("Either --image or --image-dir must be specified")
    
    if not Path(args.model).exists():
        print(f"Error: Model file not found: {args.model}")
        print("\nPlease train a model first using:")
        print("  python src/train.py --data data.yaml")
        sys.exit(1)
    
    # Initialize and run pipeline
    pipeline = ComponentAnalysisPipeline(
        model_path=args.model,
        conf_threshold=args.conf,
        padding=args.padding
    )
    
    pipeline.run_pipeline(
        image_path=args.image,
        image_dir=args.image_dir,
        output_base_dir=args.output_dir,
        extract_mpn=not args.no_ocr,
        create_visualizations=not args.no_viz
    )


if __name__ == "__main__":
    main()
