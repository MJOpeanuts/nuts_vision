#!/usr/bin/env python3
"""
OCR Script for Manufacturer Part Number (MPN) Extraction
Extracts text from cropped component images using Tesseract OCR.
"""

import argparse
import cv2
import numpy as np
import pandas as pd
import pytesseract
from pathlib import Path
from typing import List, Dict, Optional
import re
import json


class ComponentOCR:
    """OCR processor for extracting MPNs from electronic components."""
    
    def __init__(self, tesseract_config: str = "--psm 6 --oem 3"):
        """
        Initialize OCR processor.
        
        Args:
            tesseract_config: Tesseract configuration string
        """
        self.config = tesseract_config
        
    def rotate_image(self, image: np.ndarray, angle: int) -> np.ndarray:
        """
        Rotate image by specified angle.
        
        Args:
            image: Input image
            angle: Rotation angle (0, 90, 180, or 270)
            
        Returns:
            Rotated image
        """
        if angle == 0:
            return image
        elif angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            raise ValueError(f"Invalid rotation angle: {angle}. Must be 0, 90, 180, or 270")
    
    def preprocess_for_ocr(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Preprocess image for better OCR results.
        Creates multiple versions with different preprocessing.
        Enhanced version with better optimization.
        
        Args:
            image: Input image
            
        Returns:
            List of preprocessed images
        """
        preprocessed_images = []
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Resize if too small for better OCR
        h, w = gray.shape
        if h < 100 or w < 100:
            scale = max(100 / h, 100 / w)
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # 1. Contrast enhanced (CLAHE) - usually best for text
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        preprocessed_images.append(enhanced)
        
        # 2. Denoised + sharpened version
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        preprocessed_images.append(sharpened)
        
        # 3. Binary threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        preprocessed_images.append(binary)
        
        # 4. Inverted binary
        _, inv_binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        preprocessed_images.append(inv_binary)
        
        # 5. Adaptive threshold
        adaptive = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        preprocessed_images.append(adaptive)
        
        return preprocessed_images
    
    def extract_text(
        self, 
        image: np.ndarray, 
        use_multiple_preprocessing: bool = True,
        use_rotation: bool = True
    ) -> Dict[str, any]:
        """
        Extract text from image using OCR with multiple rotations.
        
        Args:
            image: Input image
            use_multiple_preprocessing: Try multiple preprocessing methods
            use_rotation: Try 4 different rotations (0, 90, 180, 270)
            
        Returns:
            Dictionary with best_text, best_confidence, and best_angle
        """
        rotation_angles = [0, 90, 180, 270] if use_rotation else [0]
        
        overall_best_text = ""
        overall_best_confidence = 0
        overall_best_angle = 0
        
        for angle in rotation_angles:
            # Rotate image
            rotated_image = self.rotate_image(image, angle)
            
            # Preprocess
            if use_multiple_preprocessing:
                preprocessed_images = self.preprocess_for_ocr(rotated_image)
            else:
                preprocessed_images = [rotated_image]
            
            # Try OCR on each preprocessed version
            for prep_img in preprocessed_images:
                try:
                    # Extract text with confidence
                    data = pytesseract.image_to_data(
                        prep_img, 
                        config=self.config,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    # Calculate average confidence
                    confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                    avg_conf = np.mean(confidences) if confidences else 0
                    
                    # Get text
                    text = pytesseract.image_to_string(prep_img, config=self.config)
                    text = text.strip()
                    
                    # Keep best result across all rotations and preprocessings
                    if avg_conf > overall_best_confidence and text:
                        overall_best_confidence = avg_conf
                        overall_best_text = text
                        overall_best_angle = angle
                        
                except Exception as e:
                    continue
        
        return {
            'text': overall_best_text,
            'confidence': overall_best_confidence,
            'angle': overall_best_angle
        }
    
    def clean_mpn(self, text: str) -> str:
        """
        Clean and format extracted MPN.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned MPN
        """
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        
        # Common patterns for MPNs (alphanumeric with possible dashes/underscores)
        # This is a simple cleanup - can be enhanced based on specific MPN formats
        text = re.sub(r'[^\w\s\-]', '', text)
        
        return text.strip()
    
    def process_component_image(
        self, 
        image_path: str,
        component_type: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Process a single component image and extract MPN.
        
        Args:
            image_path: Path to component image
            component_type: Type of component (e.g., 'IC')
            
        Returns:
            Dictionary with image path, extracted text, cleaned MPN, angle, and confidence
        """
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Extract text with rotation support
        ocr_result = self.extract_text(image, use_multiple_preprocessing=True, use_rotation=True)
        
        # Clean MPN
        cleaned_mpn = self.clean_mpn(ocr_result['text'])
        
        return {
            'image_path': str(image_path),
            'component_type': component_type or 'unknown',
            'raw_text': ocr_result['text'],
            'mpn': cleaned_mpn,
            'rotation_angle': ocr_result['angle'],
            'confidence': ocr_result['confidence']
        }
    
    def process_directory(
        self,
        input_dir: str,
        output_csv: str = "outputs/results/mpn_results.csv",
        output_json: str = "outputs/results/mpn_results.json",
        component_filter: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Process all component images in a directory.
        
        Args:
            input_dir: Directory containing component images
            output_csv: Path to output CSV file
            output_json: Path to output JSON file
            component_filter: List of component types to process (e.g., ['IC'])
            
        Returns:
            DataFrame with OCR results
        """
        input_dir = Path(input_dir)
        results = []
        
        # Find all images
        image_files = []
        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            image_files.extend(input_dir.glob(f"**/*{ext}"))
            image_files.extend(input_dir.glob(f"**/*{ext.upper()}"))
        
        print(f"Found {len(image_files)} images to process")
        
        # Process each image
        for image_path in image_files:
            # Extract component type from filename if available
            # Expected format: imagename_componenttype_N.jpg
            component_type = None
            parts = image_path.stem.split('_')
            if len(parts) >= 2:
                component_type = parts[-2]  # Component type before the number
            
            # Skip if not in filter
            if component_filter and component_type not in component_filter:
                continue
            
            print(f"Processing: {image_path.name}")
            try:
                result = self.process_component_image(str(image_path), component_type)
                results.append(result)
                if result['mpn']:
                    print(f"  MPN: {result['mpn']} (angle: {result['rotation_angle']}°, conf: {result['confidence']:.1f})")
                else:
                    print(f"  No MPN extracted")
            except Exception as e:
                print(f"  Error: {e}")
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Save results
        if not df.empty:
            # Save CSV
            output_csv_path = Path(output_csv)
            output_csv_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_csv_path, index=False)
            print(f"\nSaved CSV results to: {output_csv_path}")
            
            # Save JSON
            output_json_path = Path(output_json)
            output_json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_json_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Saved JSON results to: {output_json_path}")
        
        return df


def main():
    parser = argparse.ArgumentParser(description="Extract MPNs from component images using OCR")
    parser.add_argument(
        "--image",
        type=str,
        help="Path to single component image"
    )
    parser.add_argument(
        "--image-dir",
        type=str,
        help="Directory containing component images"
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="outputs/results/mpn_results.csv",
        help="Path to output CSV file"
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="outputs/results/mpn_results.json",
        help="Path to output JSON file"
    )
    parser.add_argument(
        "--filter",
        type=str,
        nargs='+',
        default=['IC'],
        help="Component types to process (default: IC only)"
    )
    parser.add_argument(
        "--tesseract-config",
        type=str,
        default="--psm 6 --oem 3",
        help="Tesseract configuration string"
    )
    
    args = parser.parse_args()
    
    if not args.image and not args.image_dir:
        parser.error("Either --image or --image-dir must be specified")
    
    # Initialize OCR processor
    ocr = ComponentOCR(tesseract_config=args.tesseract_config)
    
    # Process images
    if args.image:
        result = ocr.process_component_image(args.image)
        print(f"\nResults for {args.image}:")
        print(f"  Raw text: {result['raw_text']}")
        print(f"  Cleaned MPN: {result['mpn']}")
    else:
        ocr.process_directory(
            args.image_dir,
            output_csv=args.output_csv,
            output_json=args.output_json,
            component_filter=args.filter
        )


if __name__ == "__main__":
    main()
