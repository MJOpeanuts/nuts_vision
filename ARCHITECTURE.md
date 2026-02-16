# Architecture Overview - nuts_vision

This document describes the architecture and design of the nuts_vision system.

## System Overview

nuts_vision is a modular computer vision system for electronic component detection and OCR. The system is designed with a pipeline architecture where each module can be used independently or as part of the complete workflow.

```
┌─────────────────┐
│  Input Image(s) │
└────────┬────────┘
         │
         ▼
┌────────────────────────────┐
│  1. Component Detection    │
│  (detect.py)               │
│  - Gaussian blur           │
│  - Edge detection          │
│  - YOLO inference          │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│  2. Component Cropping     │
│  (crop.py)                 │
│  - Extract bounding boxes  │
│  - Apply padding           │
│  - Save individual images  │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│  3. OCR/MPN Extraction     │
│  (ocr.py)                  │
│  - Image preprocessing     │
│  - Tesseract OCR           │
│  - MPN cleaning            │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│  4. Visualization          │
│  (visualize.py)            │
│  - Statistics plots        │
│  - Result grids            │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│  Outputs:                  │
│  - Detections (JSON)       │
│  - Cropped images          │
│  - MPNs (CSV/JSON)         │
│  - Visualizations (PNG)    │
└────────────────────────────┘
```

## Module Architecture

### 1. Training Module (train.py)

**Purpose**: Train YOLOv8 models on the CompDetect dataset

**Key Components**:
- Model initialization (supports nano to xlarge)
- Training configuration
- Validation metrics
- Checkpoint saving

**Inputs**:
- Dataset (YOLO format)
- data.yaml configuration
- Training hyperparameters

**Outputs**:
- Trained model weights (best.pt, last.pt)
- Training plots
- Validation metrics

### 2. Detection Module (detect.py)

**Purpose**: Detect electronic components in images

**Class**: `ComponentDetector`

**Key Methods**:
- `preprocess_image()`: Apply Gaussian blur and edge detection
- `detect_components()`: Run YOLO inference on single image
- `batch_detect()`: Process multiple images

**Preprocessing Pipeline**:
1. Gaussian blur (reduces noise)
2. Optional edge detection (for visualization)
3. YOLO inference
4. Post-processing (NMS, confidence filtering)

**Inputs**:
- Circuit board images
- Trained YOLO model
- Detection parameters (confidence, preprocessing options)

**Outputs**:
- Detection results (JSON)
- Annotated images
- Bounding box coordinates

**Detection Result Format**:
```json
{
  "class_id": 0,
  "class_name": "IC",
  "confidence": 0.95,
  "bbox": [x1, y1, x2, y2],
  "bbox_center": [x_center, y_center, width, height]
}
```

### 3. Cropping Module (crop.py)

**Purpose**: Extract individual components from board images

**Class**: `ComponentCropper`

**Key Methods**:
- `crop_component()`: Crop single component with padding
- `crop_from_detections()`: Crop all components from image
- `crop_from_detection_file()`: Batch crop from detection results

**Process**:
1. Load detection results
2. For each detection:
   - Extract bounding box coordinates
   - Add configurable padding
   - Clip to image boundaries
   - Save cropped image with descriptive name

**Naming Convention**:
```
{image_name}_{component_type}_{index}.jpg
Example: board1_IC_0.jpg
```

**Metadata**:
Each cropping operation generates metadata containing:
- Original image path
- Cropped image path
- Component type
- Detection confidence
- Bounding box coordinates

### 4. OCR Module (ocr.py)

**Purpose**: Extract manufacturer part numbers from component images

**Class**: `ComponentOCR`

**Key Methods**:
- `preprocess_for_ocr()`: Apply multiple preprocessing strategies
- `extract_text()`: Run Tesseract OCR
- `clean_mpn()`: Clean and format extracted text
- `process_directory()`: Batch process components

**OCR Preprocessing Strategies**:
1. Original grayscale
2. Binary threshold (Otsu)
3. Inverted binary threshold
4. Adaptive threshold
5. Denoised (Non-local means)
6. Contrast enhanced (CLAHE)

The system tries all strategies and selects the result with highest confidence.

**MPN Cleaning**:
- Remove extra whitespace
- Filter non-alphanumeric characters (preserving dashes)
- Standardize format

**Inputs**:
- Cropped component images
- Component type filter (e.g., ICs only)
- Tesseract configuration

**Outputs**:
- CSV file with extracted MPNs
- JSON file with detailed results
- Confidence scores

**OCR Result Format**:
```csv
image_path,component_type,raw_text,mpn
path/to/IC_0.jpg,IC,"LM358N",LM358N
```

### 5. Visualization Module (visualize.py)

**Purpose**: Generate statistics and visualizations

**Class**: `DetectionVisualizer`

**Key Methods**:
- `plot_detection_statistics()`: Component counts, confidence distributions
- `plot_ocr_results()`: OCR success rates, MPN statistics
- `create_annotated_grid()`: Grid of annotated images

**Generated Visualizations**:
1. **Detection Statistics**:
   - Component type distribution
   - Confidence score histogram
   - Average confidence by type
   - Components per image

2. **OCR Results**:
   - Success rate by component type
   - MPN length distribution

**Outputs**:
- PNG images with plots
- High resolution (300 DPI)

### 6. Pipeline Module (pipeline.py)

**Purpose**: Orchestrate the complete workflow

**Class**: `ComponentAnalysisPipeline`

**Workflow**:
1. Initialize all modules
2. Run detection
3. Crop components
4. Extract MPNs (optional)
5. Generate visualizations (optional)
6. Save all results

**Configuration**:
- Single vs batch processing
- Enable/disable OCR
- Enable/disable visualizations
- Output directory structure

## Data Flow

### Single Image Processing

```
board.jpg
   ↓
[Detection] → detections.json
   ↓
[Cropping] → board_IC_0.jpg, board_IC_1.jpg, ...
   ↓
[OCR] → mpn_results.csv
   ↓
[Visualization] → statistics.png
```

### Batch Processing

```
images/
├── board1.jpg
├── board2.jpg
└── board3.jpg
   ↓
[Detection] → results/detections.json
   ↓
[Cropping] → cropped_components/
│                ├── board1_IC_0.jpg
│                ├── board1_IC_1.jpg
│                ├── board2_IC_0.jpg
│                └── ...
   ↓
[OCR] → results/mpn_results.csv
   ↓
[Visualization] → visualizations/
                     ├── detection_statistics.png
                     └── ocr_results.png
```

## Directory Structure

```
nuts_vision/
├── src/                      # Source code modules
│   ├── __init__.py          # Package initialization
│   ├── train.py             # Model training
│   ├── detect.py            # Component detection
│   ├── crop.py              # Component cropping
│   ├── ocr.py               # MPN extraction
│   ├── visualize.py         # Visualization
│   └── pipeline.py          # Complete pipeline
├── outputs/                  # Generated outputs
│   ├── results/             # Detection and OCR results
│   ├── cropped_components/  # Cropped images
│   └── visualizations/      # Plots and charts
├── models/                   # Saved model weights
├── runs/                     # Training runs (auto-generated)
├── data.yaml                # Dataset configuration
├── requirements.txt         # Python dependencies
├── README.md                # Main documentation
├── QUICKSTART.md            # Quick start guide
├── ARCHITECTURE.md          # This file
├── setup.py                 # Setup helper
├── check_dependencies.py    # Dependency checker
└── example.py               # Usage examples
```

## Technology Stack

### Core Libraries

1. **Ultralytics (YOLOv8)**
   - Object detection
   - Model training
   - Inference engine

2. **OpenCV (cv2)**
   - Image preprocessing
   - Cropping operations
   - Visualization

3. **Tesseract OCR**
   - Text extraction
   - Character recognition

4. **PyTorch**
   - Deep learning backend
   - GPU acceleration

### Supporting Libraries

- **NumPy**: Array operations
- **Pandas**: Data management
- **Matplotlib/Seaborn**: Visualization
- **Pillow**: Image I/O
- **PyYAML**: Configuration

## Performance Considerations

### Training
- **GPU**: Highly recommended (10-100x faster)
- **Memory**: 8GB+ RAM, 4GB+ VRAM
- **Time**: 30 minutes to several hours depending on epochs and model size

### Inference
- **Speed**: ~10-50 images/second (GPU), ~1-5 images/second (CPU)
- **Memory**: ~2GB RAM minimum

### OCR
- **Speed**: ~0.5-2 seconds per component
- **Accuracy**: 70-95% depending on image quality

## Extension Points

### Adding New Component Types

1. Update dataset with new annotations
2. Modify `data.yaml` to include new classes
3. Retrain model
4. No code changes needed

### Custom OCR Preprocessing

Extend `ComponentOCR.preprocess_for_ocr()`:
```python
def preprocess_for_ocr(self, image):
    preprocessed = super().preprocess_for_ocr(image)
    # Add custom preprocessing
    custom_image = my_preprocessing(image)
    preprocessed.append(custom_image)
    return preprocessed
```

### Custom Visualization

Extend `DetectionVisualizer`:
```python
class CustomVisualizer(DetectionVisualizer):
    def plot_custom_metric(self, data):
        # Add custom plots
        pass
```

## Design Principles

1. **Modularity**: Each module can be used independently
2. **Flexibility**: Configuration through command-line arguments
3. **Extensibility**: Classes designed for inheritance
4. **Robustness**: Error handling and validation
5. **Usability**: Clear documentation and examples

## Best Practices

### For Best Detection Results
- Use high-resolution images (640x640 or larger)
- Ensure good lighting in source images
- Train with diverse dataset
- Adjust confidence threshold based on use case

### For Best OCR Results
- Crop with adequate padding (10-20 pixels)
- Use higher resolution images
- Filter to relevant component types (ICs)
- Clean and validate extracted text

### For Production Use
- Use medium or large YOLO models (m, l)
- Implement batch processing
- Save intermediate results
- Monitor performance metrics
- Version control models and datasets

## Future Enhancements

Potential areas for improvement:
- GPU batch inference optimization
- Real-time video processing
- Web interface
- API server
- Mobile deployment
- Active learning for dataset improvement
- Multi-language OCR support
- Component database integration

## Troubleshooting

See the main README.md for common issues and solutions.

## References

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [CompDetect Dataset](https://app.roboflow.com/peanuts-q9amc/compdetect-f6vw8/3)
