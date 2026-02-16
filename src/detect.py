#!/usr/bin/env python3
"""
Component Detection Script with Image Preprocessing
Detects electronic components in circuit board images using YOLO and preprocessing.
"""

import argparse
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from typing import List, Tuple, Optional
import json


class ComponentDetector:
    """Detector for electronic components on circuit boards."""
    
    def __init__(self, model_path: str, conf_threshold: float = 0.25):
        """
        Initialize the component detector.
        
        Args:
            model_path: Path to the trained YOLO model
            conf_threshold: Confidence threshold for detections
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        
    def preprocess_image(
        self, 
        image: np.ndarray,
        apply_blur: bool = True,
        blur_kernel: Tuple[int, int] = (5, 5),
        detect_edges: bool = False
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess image with Gaussian blur and edge detection.
        
        Args:
            image: Input image (BGR format)
            apply_blur: Whether to apply Gaussian blur
            blur_kernel: Kernel size for Gaussian blur
            detect_edges: Whether to detect edges
            
        Returns:
            Tuple of (preprocessed_image, edge_map)
        """
        preprocessed = image.copy()
        
        # Apply Gaussian blur to reduce noise
        if apply_blur:
            preprocessed = cv2.GaussianBlur(preprocessed, blur_kernel, 0)
        
        # Detect edges (optional, for visualization)
        edge_map = None
        if detect_edges:
            gray = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2GRAY)
            edge_map = cv2.Canny(gray, 50, 150)
        
        return preprocessed, edge_map
    
    def detect_components(
        self, 
        image_path: str,
        preprocess: bool = True,
        save_visualization: bool = True,
        output_dir: str = "outputs/results"
    ) -> List[dict]:
        """
        Detect components in an image.
        
        Args:
            image_path: Path to input image
            preprocess: Whether to preprocess the image
            save_visualization: Whether to save annotated image
            output_dir: Directory to save results
            
        Returns:
            List of detection dictionaries
        """
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        original_image = image.copy()
        
        # Preprocess if requested
        if preprocess:
            image, edge_map = self.preprocess_image(image)
        
        # Run detection
        results = self.model(image, conf=self.conf_threshold, verbose=False)
        
        # Parse detections
        detections = []
        for result in results:
            boxes = result.boxes
            for i, box in enumerate(boxes):
                detection = {
                    'class_id': int(box.cls[0]),
                    'class_name': result.names[int(box.cls[0])],
                    'confidence': float(box.conf[0]),
                    'bbox': box.xyxy[0].cpu().numpy().tolist(),  # [x1, y1, x2, y2]
                    'bbox_center': box.xywh[0].cpu().numpy().tolist()  # [x_center, y_center, width, height]
                }
                detections.append(detection)
        
        # Save visualization if requested
        if save_visualization:
            output_path = Path(output_dir) / f"{Path(image_path).stem}_detected.jpg"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Annotate image
            annotated = results[0].plot()
            cv2.imwrite(str(output_path), annotated)
            print(f"Saved visualization to: {output_path}")
        
        return detections
    
    def batch_detect(
        self,
        image_dir: str,
        output_dir: str = "outputs/results",
        extensions: List[str] = ['.jpg', '.jpeg', '.png', '.bmp']
    ) -> dict:
        """
        Detect components in multiple images.
        
        Args:
            image_dir: Directory containing images
            output_dir: Directory to save results
            extensions: List of valid image extensions
            
        Returns:
            Dictionary mapping image paths to detections
        """
        image_dir = Path(image_dir)
        all_detections = {}
        
        # Find all images
        image_files = []
        for ext in extensions:
            image_files.extend(image_dir.glob(f"*{ext}"))
            image_files.extend(image_dir.glob(f"*{ext.upper()}"))
        
        print(f"Found {len(image_files)} images to process")
        
        # Process each image
        for image_path in image_files:
            print(f"\nProcessing: {image_path.name}")
            try:
                detections = self.detect_components(
                    str(image_path),
                    output_dir=output_dir
                )
                all_detections[str(image_path)] = detections
                print(f"  Detected {len(detections)} components")
            except Exception as e:
                print(f"  Error processing {image_path}: {e}")
        
        # Save results to JSON
        results_file = Path(output_dir) / "detections.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(all_detections, f, indent=2)
        print(f"\nSaved detection results to: {results_file}")
        
        return all_detections


def main():
    parser = argparse.ArgumentParser(description="Detect electronic components in images")
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
        default="outputs/results",
        help="Directory to save results"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold for detections"
    )
    parser.add_argument(
        "--no-preprocess",
        action="store_true",
        help="Disable image preprocessing"
    )
    
    args = parser.parse_args()
    
    if not args.image and not args.image_dir:
        parser.error("Either --image or --image-dir must be specified")
    
    # Initialize detector
    detector = ComponentDetector(args.model, conf_threshold=args.conf)
    
    # Process images
    if args.image:
        detections = detector.detect_components(
            args.image,
            preprocess=not args.no_preprocess,
            output_dir=args.output_dir
        )
        print(f"\nDetected {len(detections)} components:")
        for det in detections:
            print(f"  - {det['class_name']}: {det['confidence']:.2f}")
    else:
        detector.batch_detect(args.image_dir, args.output_dir)


if __name__ == "__main__":
    main()
