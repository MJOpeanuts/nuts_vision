# Quick Start Guide - nuts_vision

This guide will help you get started with nuts_vision quickly.

## Prerequisites

Before starting, make sure you have:
- Python 3.8 or higher
- pip (Python package manager)
- Tesseract OCR

## Step 1: Install Dependencies

### 1.1 Install Tesseract OCR

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

### 1.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 1.3 Verify Installation

```bash
python check_dependencies.py
```

## Step 2: Prepare Your Dataset

The project expects a YOLO format dataset with the following structure:

```
nuts_vision/
├── data.yaml
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

If you're using the CompDetect dataset from Roboflow, download it in YOLOv8 format and extract it to the project root.

**Important:** Update `data.yaml` if your dataset paths are different.

## Step 3: Train the Model

Train a YOLO model on your dataset:

```bash
# Quick training (nano model, good for testing)
python src/train.py --data data.yaml --model-size n --epochs 50

# Full training (recommended for production)
python src/train.py --data data.yaml --model-size m --epochs 100
```

The trained model will be saved to: `runs/detect/component_detector/weights/best.pt`

**Note:** Training can take several hours depending on your hardware and model size.

## Step 4: Process Images

### Option A: Complete Pipeline (Recommended)

Process circuit board images with a single command:

```bash
# Single image
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image path/to/board.jpg

# Multiple images
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image-dir path/to/images/
```

This will:
1. Detect all components
2. Crop each component
3. Extract MPNs from ICs
4. Generate visualizations

Results will be saved to the `outputs/` directory.

### Option B: Step-by-Step Processing

If you prefer to run each step individually:

**1. Detect Components:**
```bash
python src/detect.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image-dir path/to/images/ \
  --output-dir outputs/results
```

**2. Crop Components:**
```bash
python src/crop.py \
  --detection-file outputs/results/detections.json \
  --output-dir outputs/cropped_components
```

**3. Extract MPNs:**
```bash
python src/ocr.py \
  --image-dir outputs/cropped_components \
  --output-csv outputs/results/mpn_results.csv \
  --filter IC
```

**4. Create Visualizations:**
```bash
python src/visualize.py \
  --detection-file outputs/results/detections.json \
  --ocr-csv outputs/results/mpn_results.csv \
  --output-dir outputs/visualizations
```

## Step 5: View Results

Check the following output files:

1. **Detection Results:**
   - `outputs/results/detections.json` - All detections with bounding boxes
   - `outputs/results/*_detected.jpg` - Annotated images

2. **Cropped Components:**
   - `outputs/cropped_components/` - Individual component images

3. **MPN Extraction:**
   - `outputs/results/mpn_results.csv` - Extracted manufacturer part numbers
   - `outputs/results/mpn_results.json` - Same data in JSON format

4. **Visualizations:**
   - `outputs/visualizations/detection_statistics.png` - Detection statistics
   - `outputs/visualizations/ocr_results.png` - OCR performance

## Common Issues

### "No module named 'ultralytics'"
Run: `pip install -r requirements.txt`

### "Tesseract not found"
Install Tesseract OCR (see Step 1.1)

### "CUDA out of memory"
Use a smaller model or reduce batch size:
```bash
python src/train.py --model-size n --batch 8
```

### Poor OCR Results
- Use higher resolution images
- Adjust confidence threshold: `--conf 0.5`
- Increase crop padding: `--padding 20`

## Next Steps

- **Fine-tune the model**: Adjust hyperparameters in training
- **Custom components**: Add your own component classes to `data.yaml`
- **Improve OCR**: Experiment with different Tesseract configurations
- **Integrate**: Use the Python API in your own scripts (see `example.py`)

## Getting Help

- Check the main README.md for detailed documentation
- Run any script with `--help` for usage information
- Review `example.py` for code examples

## Example Workflow

Here's a complete example workflow:

```bash
# 1. Check dependencies
python check_dependencies.py

# 2. Train model (if not already trained)
python src/train.py --data data.yaml --epochs 100

# 3. Process your board images
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image-dir my_boards/ \
  --output-dir results/

# 4. View results
ls results/
cat results/results/mpn_results.csv
```

That's it! You're now ready to analyze electronic circuit boards with nuts_vision.
