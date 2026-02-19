# nuts_vision

Automated electronic circuit board analyser — upload a photo of a PCB, detect every component with YOLOv8, crop each one individually, and browse the results through a Streamlit web interface.

## What the application does

1. **Upload** one or more PCB photos via the web interface.
2. **Detect** — a YOLOv8 model identifies and classifies every component on the board (16 classes).
3. **Crop** — each detected component is saved as a separate image.
4. **Browse** — every analysis is stored as a *job* (its own folder) that you can review in the **Job Viewer** page.
5. **Log** *(optional)* — all results can be stored in a PostgreSQL database for later querying and statistics.

### Detectable component classes

IC, LED, Battery, Buzzer, Capacitor, Clock, Connector, Diode, Display, Fuse, Inductor, Potentiometer, Relay, Resistor, Switch, Transistor.

---

## Project structure

```
nuts_vision/
├── app.py                  # Streamlit web interface (main entry point)
├── requirements.txt        # Python dependencies
├── data.yaml               # YOLO dataset configuration
├── .env.example            # Example environment variables
├── docker-compose.yml      # PostgreSQL container (optional)
├── start_web.sh / .bat     # Convenience launchers
├── setup.py                # Project setup helper
├── check_dependencies.py   # Dependency checker
├── example.py              # Python usage examples
├── README.md               # This file
├── YOLO_MODEL.md           # YOLO model details, training and replacement
├── README.roboflow.txt     # Dataset attribution
├── src/
│   ├── pipeline.py         # Full detect + crop pipeline
│   ├── detect.py           # Component detector (YOLOv8 wrapper)
│   ├── crop.py             # Component cropper
│   ├── train.py            # Model training script
│   ├── visualize.py        # Visualization utilities
│   └── database.py         # PostgreSQL logging (optional)
└── database/
    └── init.sql            # Database schema
```

### Job output structure

Each processed image produces a job folder:

```
jobs/
  <image_name>_<YYYYMMDD>_<HHMMSS>/
    input.<ext>     — original photo
    result.jpg      — annotated photo with bounding boxes
    crops/          — one cropped image per detected component
    metadata.json   — detection data (class, confidence, bbox, crop filename)
```

---

## Installation

**Requirements:** Python 3.8+, Docker (optional, for the database).

```bash
# Install Python dependencies
pip install -r requirements.txt
```

---

## Running the web interface

```bash
# Quickest way (handles venv + .env automatically)
bash start_web.sh          # Linux / macOS
start_web.bat              # Windows

# Or launch directly
streamlit run app.py
```

Open your browser at **http://localhost:8501**.

### Web interface pages

| Page | Description |
|------|-------------|
| 🏠 Home | Overview and quick statistics |
| 📤 Upload & Process | Upload PCB images and run the detection pipeline |
| 🔍 Job Viewer | Browse per-job results: input photo, annotated result, crops, metadata |
| 🗄️ Database Viewer | Browse the PostgreSQL database tables (requires DB) |
| 📊 Statistics | Component counts and job history charts (requires DB) |
| ℹ️ About | Version and environment info |

---

## Running from the command line

```bash
# Process a single image
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image path/to/board.jpg

# Process a whole directory
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image-dir path/to/images/

# With database logging
python src/pipeline.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image path/to/board.jpg \
  --use-database
```

---

## Optional: PostgreSQL database

The database is entirely optional. Without it, all results are still saved to the `jobs/` folder.

```bash
# Start the database container
docker-compose up -d

# Copy and edit the environment file
cp .env.example .env   # adjust credentials if needed
```

The `.env` variables used:

| Variable | Default |
|----------|---------|
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `nuts_vision` |
| `DB_USER` | `nuts_user` |
| `DB_PASSWORD` | `nuts_password` |

---

## YOLO model

The detection model is a **YOLOv8** model trained on the **CompDetect v3** dataset (583 annotated PCB images, 16 classes, CC BY 4.0).

See **[YOLO_MODEL.md](YOLO_MODEL.md)** for full details on:
- where the model file is located in the project
- how to train a new model from scratch
- how to swap in a custom or pre-trained model

---

## Dataset

**CompDetect v3** — sourced from Roboflow  
Workspace: `peanuts-q9amc` · Project: `compdetect-f6vw8` · Version 3  
License: CC BY 4.0  
See `README.roboflow.txt` and `data.yaml` for full details.

---

## License

CC BY 4.0 — same terms as the CompDetect dataset.