# nuts_vision - Electronic Component Detection & OCR

A computer vision system for automated electronic circuit board analysis using YOLOv8 and Tesseract OCR. Now with integrated Arducam 108MP motorized focus camera support for high-quality image capture.

> 🚀 **[START HERE / COMMENCER ICI](COMMENCER_ICI.md)** - Get started in 5 minutes!
> 
> 🇫🇷 [Version française / French version](README_FR.md) | [Démarrage rapide](DEMARRAGE_RAPIDE.md)
> 
> 🇬🇧 [Quick Start Guide](QUICKSTART.md) | 📷 [Camera Guide](CAMERA.md)

## Overview

This project uses computer vision to analyze images of electronic circuit boards, detect and automatically crop individual components (ICs, resistors, capacitors, etc.), and extract Manufacturer Part Numbers (MPNs) via OCR. The system is built on a YOLO model trained on the CompDetect dataset (583 images, 16 component classes).

**New:** Full integration with Arducam 108MP camera (ref: B0494C) for capturing high-resolution photos with automatic focus control.

### Key Features

- **🌐 Web Interface**: Modern Streamlit-based GUI with Supabase-like database viewer
- **📷 Arducam Camera Support**: Integrated support for Arducam 108MP motorized focus camera
- **Component Detection**: YOLOv8-based detection of 16 component types
- **Image Preprocessing**: Gaussian blur and edge detection for improved accuracy
- **Smart IC Cropping**: Automatically crops only IC components for OCR processing
- **Advanced OCR**: Multi-angle OCR (0°, 90°, 180°, 270°) with image optimization for better text extraction
- **MPN Extraction**: Manufacturer part number extraction from ICs with confidence scoring
- **Database Tracking**: PostgreSQL database with Supabase-like interface for tracking all operations
- **CSV Export**: Save extracted MPNs for inventory management
- **Visualization**: Generate statistics and visualizations of detection results

### Component Classes

The model can detect the following 16 component types:
- IC (Integrated Circuit)
- LED
- Battery
- Buzzer
- Capacitor
- Clock
- Connector
- Diode
- Display
- Fuse
- Inductor
- Potentiometer
- Relay
- Resistor
- Switch
- Transistor

## Installation

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR (for MPN extraction)
- Docker (optional, for database tracking)

### Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Train the Model

First, ensure you have the dataset ready, then train the YOLO model:

```bash
python src/train.py --data data.yaml --epochs 100 --model-size n
```

This will create a trained model at `runs/detect/component_detector/weights/best.pt`

### 2. Run the Complete Pipeline

Process circuit board images and extract component information:

```bash
# Process a single image
python src/pipeline.py --model runs/detect/component_detector/weights/best.pt --image path/to/board.jpg

# Process a directory of images
python src/pipeline.py --model runs/detect/component_detector/weights/best.pt --image-dir path/to/images/
```

This will:
1. Detect all components in the image(s)
2. Crop only IC components for OCR processing
3. Extract MPNs from ICs using multi-angle OCR (0°, 90°, 180°, 270°)
4. Generate visualizations and statistics
5. Save results to CSV and JSON files

### 3. (Optional) Enable Database Tracking

Start the PostgreSQL database and run the pipeline with database logging:

```bash
# Start database
docker-compose up -d

# Run pipeline with database tracking
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image path/to/board.jpg \
  --use-database
```

See [DATABASE.md](DATABASE.md) for database setup and [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for more examples.

### 4. (Optional) Capture Images with Arducam Camera

nuts_vision now supports the Arducam 108MP Motorized Focus USB 3.0 Camera (ref: B0494C).

**Using the Web Interface:**

1. Start the web interface: `streamlit run app.py`
2. Navigate to the **📷 Camera Control** page
3. Connect to your camera
4. Adjust focus (manual or automatic)
5. Capture high-resolution photos
6. Process photos through the detection pipeline

**Using Python:**

```python
from src.camera_control import ArducamCamera
from src.pipeline import ComponentAnalysisPipeline

# Connect to camera
camera = ArducamCamera(camera_index=0)
if camera.connect(width=1920, height=1080):
    # Auto-focus
    camera.auto_focus_scan()
    
    # Capture photo
    photo_path = camera.capture_photo()
    
    # Process with pipeline
    pipeline = ComponentAnalysisPipeline(model_path="runs/detect/component_detector/weights/best.pt")
    results = pipeline.process_image(photo_path)
    
    camera.disconnect()
```

📚 **Additional Guides:**
- [CAMERA.md](CAMERA.md) - Complete camera documentation
- [ARDUCAM_OPTIMIZATION.md](ARDUCAM_OPTIMIZATION.md) - ⭐ **Optimizations for dark images and jerky preview**
- [ARDUCAM_108MP_CONFIG.md](ARDUCAM_108MP_CONFIG.md) - Camera specifications and configuration

## Detailed Usage

### Training

Train a YOLO model for component detection:

```bash
python src/train.py \
  --data data.yaml \
  --model-size n \
  --epochs 100 \
  --batch 16 \
  --imgsz 640
```

**Arguments:**
- `--data`: Path to data.yaml configuration file
- `--model-size`: Model size (n=nano, s=small, m=medium, l=large, x=xlarge)
- `--epochs`: Number of training epochs
- `--batch`: Batch size
- `--imgsz`: Input image size

### Detection

Detect components in images:

```bash
# Single image
python src/detect.py --model path/to/best.pt --image board.jpg

# Batch processing
python src/detect.py --model path/to/best.pt --image-dir images/ --conf 0.3
```

**Arguments:**
- `--model`: Path to trained YOLO model
- `--image`: Single image path
- `--image-dir`: Directory of images
- `--conf`: Confidence threshold (default: 0.25)
- `--no-preprocess`: Disable image preprocessing

### Component Cropping

Crop detected components from images:

```bash
python src/crop.py \
  --detection-file outputs/results/detections.json \
  --output-dir outputs/cropped_components \
  --padding 10
```

**Arguments:**
- `--detection-file`: Path to detections.json from detection step
- `--output-dir`: Directory to save cropped components
- `--padding`: Padding around components in pixels

### OCR / MPN Extraction

Extract manufacturer part numbers from component images:

```bash
python src/ocr.py \
  --image-dir outputs/cropped_components \
  --output-csv outputs/results/mpn_results.csv \
  --filter IC
```

**Arguments:**
- `--image-dir`: Directory containing cropped component images
- `--output-csv`: Path to output CSV file
- `--filter`: Component types to process (default: IC only)

### Visualization

Generate statistics and visualizations:

```bash
python src/visualize.py \
  --detection-file outputs/results/detections.json \
  --ocr-csv outputs/results/mpn_results.csv \
  --output-dir outputs/visualizations
```

## Project Structure

```
nuts_vision/
├── data.yaml                    # Dataset configuration
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── README.roboflow.txt         # Dataset information
├── src/
│   ├── train.py                # YOLO model training
│   ├── detect.py               # Component detection
│   ├── crop.py                 # Component cropping
│   ├── ocr.py                  # MPN extraction via OCR
│   ├── visualize.py            # Visualization utilities
│   └── pipeline.py             # Complete pipeline
├── outputs/
│   ├── results/                # Detection results (JSON, CSV)
│   ├── cropped_components/     # Cropped component images
│   └── visualizations/         # Generated plots
└── models/                     # Saved models
```

## Output Files

The pipeline generates several output files:

1. **detections.json**: Detection results with bounding boxes and confidence scores
2. **mpn_results.csv**: Extracted MPNs with metadata
3. **mpn_results.json**: MPN results in JSON format
4. **Cropped images**: Individual component images in `cropped_components/`
5. **Visualizations**: Statistical plots in `visualizations/`

### Example CSV Output

```csv
image_path,component_type,raw_text,mpn
/path/to/IC_0.jpg,IC,LM358N,LM358N
/path/to/IC_1.jpg,IC,74HC595,74HC595
```

## Use Cases

- **Quality Control**: Automated inspection of assembled circuit boards
- **Inventory Management**: Extract component lists from board images
- **Reverse Engineering**: Identify components on existing boards
- **Documentation**: Create component catalogs from board images
- **Education**: Learn about electronic components and computer vision

## Dataset Information

This project uses the **CompDetect v3** dataset from Roboflow:
- **Images**: 583 annotated images
- **Classes**: 16 component types
- **Format**: YOLOv8
- **License**: CC BY 4.0

For more information, see `README.roboflow.txt`

## Performance Tips

1. **Model Size**: Use larger models (m, l, x) for better accuracy
2. **Confidence Threshold**: Adjust based on your needs (higher = fewer false positives)
3. **Image Quality**: Higher resolution images yield better OCR results
4. **Preprocessing**: Enable preprocessing for noisy images
5. **Batch Size**: Reduce if you encounter memory issues

## Troubleshooting

### Tesseract not found
Make sure Tesseract OCR is installed and in your PATH. Test with:
```bash
tesseract --version
```

### CUDA out of memory
Reduce batch size or use a smaller model:
```bash
python src/train.py --model-size n --batch 8
```

### Poor OCR results
The new multi-angle OCR should significantly improve results by trying 4 different rotations. If still having issues:
- Ensure cropped images have sufficient resolution (automatically scaled to min 100x100)
- Check the rotation angle reported in results - it shows which orientation worked best
- Review the confidence scores in the output
- The system now uses enhanced preprocessing (CLAHE, denoising, sharpening)

### Database connection failed
If you see database connection errors:
- Ensure Docker is running: `docker-compose ps`
- Check database logs: `docker-compose logs postgres`
- Verify environment variables in `.env` file
- See [DATABASE.md](DATABASE.md) for detailed troubleshooting

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is licensed under the same terms as the CompDetect dataset (CC BY 4.0).

## Acknowledgments

- YOLOv8 by Ultralytics
- CompDetect dataset by Roboflow
- Tesseract OCR by Google

## Citation

If you use this project in your research, please cite:

```bibtex
@software{nuts_vision,
  title={nuts_vision: Electronic Component Detection and OCR},
  author={nuts_vision contributors},
  year={2026},
  url={https://github.com/MJOpeanuts/nuts_vision}
}
```