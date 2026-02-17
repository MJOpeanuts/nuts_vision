#!/usr/bin/env python3
"""
Complete Pipeline for Electronic Component Detection and OCR
Combines detection, cropping, and OCR into a single workflow.
Includes database logging for tracing extractions.
"""

import argparse
from pathlib import Path
import sys
import os

# Import our modules
from detect import ComponentDetector
from crop import ComponentCropper
from ocr import ComponentOCR
from visualize import DetectionVisualizer

# Import database module if available
try:
    from database import DatabaseManager, get_db_manager_from_env
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("Warning: Database module not available. Install psycopg2 to enable database logging.")


class ComponentAnalysisPipeline:
    """Complete pipeline for component detection and MPN extraction."""
    
    def __init__(
        self,
        model_path: str,
        conf_threshold: float = 0.25,
        padding: int = 10,
        use_database: bool = False
    ):
        """
        Initialize the pipeline.
        
        Args:
            model_path: Path to trained YOLO model
            conf_threshold: Confidence threshold for detections
            padding: Padding for cropped components
            use_database: Whether to log to database
        """
        self.detector = ComponentDetector(model_path, conf_threshold)
        self.cropper = ComponentCropper(padding)
        self.ocr = ComponentOCR()
        self.visualizer = DetectionVisualizer()
        self.use_database = use_database and DB_AVAILABLE
        self.model_path = model_path
        
        if self.use_database:
            try:
                self.db = get_db_manager_from_env()
                if not self.db.test_connection():
                    print("Warning: Database connection failed. Continuing without database logging.")
                    self.use_database = False
            except Exception as e:
                print(f"Warning: Could not initialize database: {e}")
                self.use_database = False
        
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
        if self.use_database:
            print("Database logging: ENABLED")
        print("="*60)
        
        # Determine images to process
        images_to_process = []
        if image_path:
            images_to_process = [image_path]
        elif image_dir:
            image_dir = Path(image_dir)
            for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                images_to_process.extend(image_dir.glob(f"*{ext}"))
                images_to_process.extend(image_dir.glob(f"*{ext.upper()}"))
            images_to_process = [str(p) for p in images_to_process]
        
        # Process each image
        all_detection_dict = {}
        
        for img_path in images_to_process:
            img_path_str = str(img_path)
            
            # Database: Log image upload
            image_id = None
            job_id = None
            if self.use_database:
                try:
                    file_name = Path(img_path_str).name
                    format = Path(img_path_str).suffix[1:]  # Remove the dot
                    image_id = self.db.log_image_upload(file_name, img_path_str, format)
                    job_id = self.db.start_job(image_id, self.model_path)
                except Exception as e:
                    print(f"Warning: Database logging failed for image upload: {e}")
            
            # Step 1: Detection
            print(f"\n[STEP 1/4] Running component detection on {Path(img_path_str).name}...")
            print("-"*60)
            
            detections = self.detector.detect_components(
                img_path_str,
                output_dir=str(results_dir)
            )
            all_detection_dict[img_path_str] = detections
            print(f"Detected {len(detections)} components")
            
            # Database: Log detections
            detection_ids = {}
            if self.use_database and job_id:
                try:
                    for i, detection in enumerate(detections):
                        det_id = self.db.log_detection(
                            job_id,
                            detection['class_name'],
                            detection['confidence'],
                            detection['bbox']
                        )
                        detection_ids[i] = det_id
                except Exception as e:
                    print(f"Warning: Database logging failed for detections: {e}")
            
            # Step 2: Cropping (only ICs for OCR)
            print("\n[STEP 2/4] Cropping IC components for OCR...")
            print("-"*60)
            
            if detections:
                cropped_paths = self.cropper.crop_from_detections(
                    img_path_str,
                    detections,
                    output_dir=str(cropped_dir),
                    component_filter=['IC']  # Only crop ICs
                )
                print(f"Cropped {len(cropped_paths)} IC components from {Path(img_path_str).name}")
                
                # Database: Log cropped ICs
                cropped_ids = {}
                if self.use_database and job_id:
                    try:
                        # Match cropped images to their detections
                        ic_index = 0
                        for i, detection in enumerate(detections):
                            if detection['class_name'] == 'IC':
                                if i in detection_ids and ic_index < len(cropped_paths):
                                    cropped_id = self.db.log_cropped_ic(
                                        job_id,
                                        detection_ids[i],
                                        cropped_paths[ic_index]
                                    )
                                    cropped_ids[cropped_paths[ic_index]] = cropped_id
                                    ic_index += 1
                    except Exception as e:
                        print(f"Warning: Database logging failed for cropped ICs: {e}")
            
            # Step 3: OCR (if requested)
            if extract_mpn and detections:
                print("\n[STEP 3/5] Extracting MPNs using OCR...")
                print("-"*60)
                
                # Process only IC images
                ic_images = [p for p in Path(cropped_dir).glob("*_IC_*.jpg")]
                for ic_image in ic_images:
                    component_type = 'IC'
                    try:
                        result = self.ocr.process_component_image(str(ic_image), component_type)
                        if result['mpn']:
                            print(f"  {ic_image.name}: {result['mpn']} (angle: {result['rotation_angle']}°, conf: {result['confidence']:.1f})")
                            
                            # Database: Log OCR result
                            if self.use_database and job_id and str(ic_image) in cropped_ids:
                                try:
                                    self.db.log_ocr_result(
                                        job_id,
                                        cropped_ids[str(ic_image)],
                                        result['raw_text'],
                                        result['mpn'],
                                        result['rotation_angle'],
                                        result['confidence']
                                    )
                                except Exception as e:
                                    print(f"Warning: Database logging failed for OCR: {e}")
                        else:
                            print(f"  {ic_image.name}: No MPN extracted")
                    except Exception as e:
                        print(f"  Error processing {ic_image.name}: {e}")
            
            # Database: End job
            if self.use_database and job_id:
                try:
                    self.db.end_job(job_id)
                except Exception as e:
                    print(f"Warning: Database logging failed for job end: {e}")
        
        # Step 4: Compile all OCR results (if requested)
        ocr_df = None
        if extract_mpn:
            print("\n[STEP 4/5] Compiling OCR results...")
            print("-"*60)
            
            ocr_df = self.ocr.process_directory(
                input_dir=str(cropped_dir),
                output_csv=str(results_dir / "mpn_results.csv"),
                output_json=str(results_dir / "mpn_results.json"),
                component_filter=['IC']
            )
            
            if not ocr_df.empty:
                successful_mpn = ocr_df[ocr_df['mpn'].notna() & (ocr_df['mpn'] != '')].shape[0]
                print(f"\nExtracted MPNs: {successful_mpn}/{len(ocr_df)}")
        else:
            print("\n[STEP 4/5] Skipping OCR compilation (--no-ocr flag set)")
        
        # Step 5: Visualization (if requested)
        if create_visualizations:
            print("\n[STEP 5/5] Creating visualizations...")
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
            print("\n[STEP 5/5] Skipping visualizations (--no-viz flag set)")
        
        # Summary
        print("\n" + "="*60)
        print("PIPELINE COMPLETE!")
        print("="*60)
        print(f"\nResults saved to: {output_base}")
        print(f"  - Detections: {results_dir}")
        print(f"  - Cropped IC components: {cropped_dir}")
        if extract_mpn:
            print(f"  - MPN extraction: {results_dir / 'mpn_results.csv'}")
        if create_visualizations:
            print(f"  - Visualizations: {viz_dir}")
        if self.use_database:
            print(f"  - Database: Logged to PostgreSQL")
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
    parser.add_argument(
        "--use-database",
        action="store_true",
        help="Enable database logging (requires PostgreSQL)"
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
        padding=args.padding,
        use_database=args.use_database
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
