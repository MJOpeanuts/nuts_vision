# Application Structure - nuts_vision Web Interface

## 🏗️ Architecture Overview

```
nuts_vision/
├── app.py                          # Main Streamlit web application
├── start_web.sh                    # Linux/Mac launcher
├── start_web.bat                   # Windows launcher
├── test_web_interface.py          # Testing script
│
├── src/
│   ├── database.py                # Enhanced database module
│   ├── pipeline.py                # Processing pipeline
│   ├── detect.py                  # Component detection
│   ├── crop.py                    # Image cropping
│   ├── ocr.py                     # OCR processing
│   └── visualize.py               # Visualization tools
│
├── database/
│   └── init.sql                   # Database schema
│
├── documentation/
│   ├── INTERFACE_WEB.md           # French web docs
│   ├── WEB_QUICKSTART.md          # Quick start guide
│   ├── WEB_IMPLEMENTATION_SUMMARY.md  # Implementation details
│   ├── README_FR.md               # French README
│   └── DATABASE.md                # Database guide
│
└── docker-compose.yml             # PostgreSQL setup
```

---

## 🌐 Web Application Flow

### User Journey:

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser: localhost:8501                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Streamlit App (app.py)                     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  🏠 Home     │  │📤 Upload &   │  │🗄️ Database   │      │
│  │  - Overview  │  │   Process    │  │   Viewer     │      │
│  │  - Stats     │  │  - Upload    │  │  - Tables    │      │
│  └──────────────┘  │  - Config    │  │  - Stats     │      │
│                    │  - Process   │  │  - Filter    │      │
│  ┌──────────────┐  └──────────────┘  └──────────────┘      │
│  │📊 Statistics │                                            │
│  │  - Metrics   │  ┌──────────────┐                        │
│  │  - Charts    │  │ℹ️ About      │                        │
│  └──────────────┘  │  - Docs      │                        │
│                    │  - System    │                        │
│                    └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               Processing Backend (src/)                      │
│                                                               │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ Detect   │→  │  Crop    │→  │   OCR    │→  │Visualize │ │
│  │ (YOLO)   │   │  (ICs)   │   │(Tesseract)│  │ (Stats)  │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│          PostgreSQL Database (via database.py)               │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │images_input │  │  log_jobs   │  │ detections  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │ics_cropped  │  │  ics_ocr    │                          │
│  └─────────────┘  └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 Page Structure

### 1. 🏠 Home Page
```
┌────────────────────────────────────┐
│ nuts_vision Logo & Title           │
├────────────────────────────────────┤
│ • System Overview                  │
│ • Key Features List                │
│ • Detectable Components (16 types) │
│ • Quick Statistics (if DB connected)│
│   - Total Images                   │
│   - Total Jobs                     │
│   - Detections                     │
│   - OCR Results                    │
│   - MPNs Extracted                 │
└────────────────────────────────────┘
```

### 2. 📤 Upload & Process Page
```
┌────────────────────────────────────┐
│ Model Configuration                │
│ [Model Path Input] [Conf Slider]   │
├────────────────────────────────────┤
│ Upload Images                      │
│ [Drag & Drop Area]                 │
│ [Browse Files Button]              │
├────────────────────────────────────┤
│ Processing Options                 │
│ ☑ Extract MPNs (OCR)               │
│ ☑ Log to Database                  │
│ ☑ Create Visualizations            │
├────────────────────────────────────┤
│ [🚀 Start Processing Button]       │
├────────────────────────────────────┤
│ Image Previews (Grid)              │
│ [Img1] [Img2] [Img3]               │
└────────────────────────────────────┘
```

### 3. 🗄️ Database Viewer Page
```
┌────────────────────────────────────┐
│ [Table Selector Dropdown]          │
│ ├─ 📸 Images Input                 │
│ ├─ 🔄 Jobs Log                     │
│ ├─ 🎯 Detections                   │
│ ├─ ✂️ Cropped ICs                  │
│ └─ 📝 OCR Results                  │
├────────────────────────────────────┤
│ [🔄 Refresh Button]                │
├────────────────────────────────────┤
│ Table Data (Paginated)             │
│ ┌──────┬──────┬──────┬──────┐     │
│ │ ID   │ Col1 │ Col2 │ Col3 │     │
│ ├──────┼──────┼──────┼──────┤     │
│ │ 1    │ ...  │ ...  │ ...  │     │
│ │ 2    │ ...  │ ...  │ ...  │     │
│ └──────┴──────┴──────┴──────┘     │
├────────────────────────────────────┤
│ Inline Statistics & Charts         │
│ (Context-specific)                 │
└────────────────────────────────────┘
```

### 4. 📊 Statistics Page
```
┌────────────────────────────────────┐
│ Overview Metrics (5 columns)       │
│ [Images] [Jobs] [Detect] [OCR] [%] │
├────────────────────────────────────┤
│ Component Distribution             │
│ ┌────────────┬─────────────┐       │
│ │ Bar Chart  │ Data Table  │       │
│ │            │             │       │
│ └────────────┴─────────────┘       │
├────────────────────────────────────┤
│ Recent Jobs                        │
│ ┌──────┬──────────┬─────────┐     │
│ │ ID   │ File     │ Detects │     │
│ └──────┴──────────┴─────────┘     │
└────────────────────────────────────┘
```

### 5. ℹ️ About Page
```
┌────────────────────────────────────┐
│ About nuts_vision                  │
│ • Key Technologies                 │
│ • Database Schema                  │
│ • Workflow Description             │
│ • Documentation Links              │
├────────────────────────────────────┤
│ System Information (2 columns)     │
│ ┌──────────────┬──────────────┐   │
│ │ Database     │ Environment  │   │
│ │ Status       │ Info         │   │
│ └──────────────┴──────────────┘   │
└────────────────────────────────────┘
```

---

## 🔄 Data Flow

### Image Upload & Processing:

```
User Upload Image
       │
       ▼
app.py receives file
       │
       ▼
Save to uploads/ directory
       │
       ▼
Create ComponentAnalysisPipeline
       │
       ▼
Log to database.images_input
       │
       ▼
Start job (database.log_jobs)
       │
       ▼
┌──────────────────────┐
│  YOLO Detection      │
│  (detect.py)         │
└──────────────────────┘
       │
       ▼
Log detections (database.detections)
       │
       ▼
┌──────────────────────┐
│  Crop ICs            │
│  (crop.py)           │
└──────────────────────┘
       │
       ▼
Log cropped (database.ics_cropped)
       │
       ▼
┌──────────────────────┐
│  OCR Processing      │
│  (ocr.py)            │
└──────────────────────┘
       │
       ▼
Log OCR results (database.ics_ocr)
       │
       ▼
End job (database.end_job)
       │
       ▼
Display results in app.py
```

### Database Query Flow:

```
User Selects Table in UI
       │
       ▼
app.py calls database method
       │
       ├─ get_all_images()
       ├─ get_all_jobs()
       ├─ get_all_detections()
       ├─ get_all_ocr_results()
       └─ get_detection_statistics()
       │
       ▼
database.py executes SQL query
       │
       ▼
PostgreSQL returns data
       │
       ▼
Format as pandas DataFrame
       │
       ▼
Display in Streamlit table
       │
       ▼
Generate inline charts/stats
```

---

## 🎨 UI Components

### Color Scheme:
- **Primary**: #1f77b4 (Blue)
- **Success**: #28a745 (Green)
- **Error**: #dc3545 (Red)
- **Background**: #ffffff (White)
- **Secondary BG**: #f0f2f6 (Light Gray)

### Custom CSS Classes:
- `.main-header` - Large page titles
- `.sub-header` - Section headers
- `.stat-box` - Metric boxes
- `.success-box` - Success messages
- `.error-box` - Error messages
- `.dataframe` - Table styling

### Icons:
- 🏠 Home
- 📤 Upload & Process
- 🗄️ Database Viewer
- 📊 Statistics
- ℹ️ About
- 📸 Images
- 🔄 Jobs
- 🎯 Detections
- ✂️ Cropped ICs
- 📝 OCR Results

---

## 🗄️ Database Tables

```
images_input
├── image_id (PK)
├── file_name
├── file_path
├── upload_at
└── format

log_jobs
├── job_id (PK)
├── image_id (FK)
├── started_at
├── ended_at
└── model

detections
├── detection_id (PK)
├── job_id (FK)
├── class_name
├── confidence
├── bbox_x1, bbox_y1
└── bbox_x2, bbox_y2

ics_cropped
├── cropped_id (PK)
├── job_id (FK)
├── detection_id (FK)
├── cropped_file_path
└── created_at

ics_ocr
├── ocr_id (PK)
├── job_id (FK)
├── cropped_id (FK)
├── raw_text
├── cleaned_mpn
├── rotation_angle
├── confidence
└── processed_at
```

---

## 🔧 Configuration Files

### .env (Environment Variables)
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nuts_vision
DB_USER=nuts_user
DB_PASSWORD=nuts_password
```

### .streamlit/config.toml (Optional)
```toml
[server]
port = 8501
maxUploadSize = 200

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
```

---

## 📚 Documentation Hierarchy

```
Documentation/
├── User Guides
│   ├── WEB_QUICKSTART.md (English)
│   ├── INTERFACE_WEB.md (French)
│   ├── README.md (English, updated)
│   └── README_FR.md (French, updated)
│
├── Technical Docs
│   ├── DATABASE.md
│   ├── ARCHITECTURE.md
│   └── WEB_IMPLEMENTATION_SUMMARY.md
│
└── Setup Guides
    ├── QUICKSTART.md
    └── DEMARRAGE_RAPIDE.md
```

---

## 🚀 Startup Process

### Automatic (start_web.sh):
```
1. Check PostgreSQL (docker-compose)
2. Start database if needed
3. Create/activate virtual environment
4. Install dependencies
5. Load .env variables
6. Launch Streamlit app
```

### Manual:
```bash
1. docker-compose up -d
2. source venv/bin/activate
3. pip install -r requirements.txt
4. streamlit run app.py
```

---

## 🎯 Key Features Summary

| Feature | Implementation | Location |
|---------|---------------|----------|
| Image Upload | Drag & drop, multi-file | app.py (Upload page) |
| Database Viewer | 5 interactive tables | app.py (Database page) |
| Statistics | Metrics + charts | app.py (Statistics page) |
| Job Tracking | Complete history | database.py + app.py |
| Real-time Updates | Refresh button | All database views |
| Filtering | By job ID | Detection/OCR tables |
| Processing Pipeline | Full integration | ComponentAnalysisPipeline |
| Cross-platform | sh + bat scripts | start_web.* |

---

**Last Updated**: 2026-02-17  
**Version**: 1.0.0
