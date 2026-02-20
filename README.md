# nuts_vision

Automated IC detector for electronic circuit boards — upload a photo of a PCB, detect every integrated circuit (IC) with YOLOv8, crop each one individually, and browse the results through a Streamlit web interface.

## What the application does

1. **Upload** one or more PCB photos via the web interface.
2. **Detect** — a YOLOv8 model (`best.pt`) identifies every IC on the board.
3. **Crop** — each detected IC is saved as a separate image.
4. **Browse** — every analysis is stored as a *job* (its own folder) that you can review in the **Job Viewer** page.
5. **Log** *(optional)* — all results can be stored in a PostgreSQL database for later querying and statistics.

### Detected component class

**IC (Integrated Circuit)** — the model was specifically trained to detect ICs on PCB images.

---

## Project structure

```
nuts_vision/
├── app.py                  # Streamlit web interface (main entry point)
├── best.pt                 # Trained YOLOv8 model (IC detection)
├── best.onnx               # ONNX export (deployment: Raspberry Pi, web, etc.)
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── docker-compose.yml      # PostgreSQL container (optional)
├── start_web.sh / .bat     # Convenience launchers
├── check_dependencies.py   # Dependency checker
├── example.py              # Python usage examples
├── README.md               # This file
├── src/
│   ├── pipeline.py         # Full detect + crop pipeline
│   ├── detect.py           # IC detector (YOLOv8 wrapper)
│   ├── crop.py             # Component cropper
│   ├── visualize.py        # Visualization utilities
│   └── database.py         # PostgreSQL logging (optional)
└── database/
    └── init.sql            # Database schema
```

### Auto-generated and dataset directories

The following directories are **not tracked by git** (they are listed in `.gitignore`) and can be safely deleted at any time:

| Directory | Origin | Can be deleted? |
|-----------|--------|----------------|
| `outputs/` | Created automatically when running the CLI scripts (`detect.py`, `crop.py`, `visualize.py`, `example.py`) to store results | ✅ Yes — recreated on next run |
| `runs/` | Created automatically by YOLO/Ultralytics during training or inference | ✅ Yes — recreated by YOLO |
| `train/` | YOLO training dataset (images + labels) | ✅ Yes — only needed to retrain the model |
| `valid/` | YOLO validation dataset (images + labels) | ✅ Yes — only needed to retrain the model |
| `test/` | YOLO test dataset (images + labels) | ✅ Yes — only needed to retrain the model |

> **Note:** The web app (`app.py`) does not use `train/`, `valid/`, `test/`, or `runs/`. It stores its results in the `jobs/` folder instead.

### Job output structure

Each processed image produces a job folder:

```
jobs/
  <image_name>_<YYYYMMDD>_<HHMMSS>/
    input.<ext>     — original photo
    result.jpg      — annotated photo with bounding boxes
    crops/          — one cropped image per detected IC
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
| 📊 Statistics | IC counts and job history charts (requires DB) |
| ℹ️ About | Version and environment info |

---

## Running from the command line

```bash
# Process a single image
python src/pipeline.py --model best.pt --image path/to/board.jpg

# Process a whole directory
python src/pipeline.py --model best.pt --image-dir path/to/images/

# With database logging
python src/pipeline.py --model best.pt --image path/to/board.jpg --use-database
```

---

## Optional: PostgreSQL database

The database is entirely optional. Without it, all results are still saved to the `jobs/` folder.

### Full Docker deployment (app + database)

```bash
# Start everything with Docker (app on port 8501 + PostgreSQL)
docker-compose up -d
```

Open your browser at **http://localhost:8501**.

The `web` service automatically sets `DB_HOST=postgres` so it connects to the database container.

### Local app + Docker database

```bash
# Start only the database container
docker-compose up -d postgres

# Copy and edit the environment file
cp .env.example .env   # keep DB_HOST=localhost for local app

# Launch the app locally
streamlit run app.py
```

The `.env` variables used:

| Variable | Default | Docker value |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | `postgres` |
| `DB_PORT` | `5432` | `5432` |
| `DB_NAME` | `nuts_vision` | `nuts_vision` |
| `DB_USER` | `nuts_user` | `nuts_user` |
| `DB_PASSWORD` | `nuts_password` | `nuts_password` |

---

## YOLO model

The detection model is a **YOLOv8** model specifically trained to detect **integrated circuits (ICs)** on PCB images.

Two model formats are included:
- **`best.pt`** — PyTorch native model for local inference with Python
- **`best.onnx`** — Universal ONNX format optimised for deployment (Raspberry Pi, web, Supabase, etc.)

---

## License

CC BY 4.0
