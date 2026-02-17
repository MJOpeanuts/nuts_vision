# Quick Start Guide - nuts_vision Web Interface

## 🚀 Getting Started in 4 Steps

### Step 0: Install Dependencies (First Time Only)

```bash
# Install web interface dependencies
pip install streamlit fastapi psycopg2-binary

# Or install all dependencies from requirements.txt
pip install -r requirements.txt

# Verify installation
python check_dependencies.py
```

### Step 1: Start the Database

```bash
# Using Docker (Recommended)
docker-compose up -d

# Or manually setup PostgreSQL
# See DATABASE.md for details
```

### Step 2: Launch the Web Interface

```bash
# Linux/Mac
./start_web.sh

# Windows
start_web.bat

# Or manually
streamlit run app.py
```

### Step 3: Open Your Browser

The application will automatically open at:
```
http://localhost:8501
```

---

## 📖 Using the Web Interface

### 🏠 Home Page

- View system overview
- Check database connection status
- See quick statistics
- Access documentation

### 📤 Upload & Process

1. **Configure Model**
   - Model Path: `runs/detect/component_detector/weights/best.pt`
   - Confidence Threshold: 0.25 (adjustable)

2. **Upload Images**
   - Click "Browse files" or drag and drop
   - Supported formats: JPG, JPEG, PNG
   - Multiple images supported

3. **Processing Options**
   - ✅ Extract MPNs (OCR) - Enable OCR processing
   - ✅ Log to Database - Save results to PostgreSQL
   - ✅ Create Visualizations - Generate charts

4. **Start Processing**
   - Click "🚀 Start Processing"
   - Monitor progress in real-time
   - View results summary

### 🗄️ Database Viewer (Supabase-like)

**Available Tables:**

#### 📸 Images Input
View all uploaded images with metadata:
- Image ID
- File name and path
- Upload timestamp
- File format

#### 🔄 Jobs Log
Complete job execution history:
- Job ID and status
- Start/end timestamps
- Model used
- Number of detections
- **Select a job to view detailed statistics**

#### 🎯 Detections
All component detections:
- Detection ID
- Component type (IC, LED, etc.)
- Confidence score
- Bounding box coordinates
- **Filter by job ID**
- **View component distribution chart**

#### ✂️ Cropped ICs
Cropped integrated circuit images:
- Cropped image ID
- Link to detection
- File path
- Creation timestamp

#### 📝 OCR Results
Text extraction results:
- OCR ID
- Raw text extracted
- Cleaned MPN (part number)
- Rotation angle used
- Confidence score
- **Success rate metrics**

**Features:**
- 🔄 Refresh button to update data
- 📊 Inline statistics and charts
- 🔍 Filter by job ID
- 📈 Component distribution graphs
- ✅ Success rate calculations

### 📊 Statistics

**Overview Metrics:**
- Total images processed
- Total jobs executed
- Total detections
- OCR results count
- MPN extraction success rate

**Component Distribution:**
- Bar chart of component types
- Detailed count table
- Interactive visualizations

**Recent Jobs:**
- Last 10 jobs processed
- File names
- Detection counts

### ℹ️ About

- System information
- Database connection status
- Environment details
- Documentation links
- Technology stack

---

## 💡 Common Use Cases

### Use Case 1: Analyze a Single PCB

1. Go to "📤 Upload & Process"
2. Upload your PCB image
3. Keep default settings
4. Click "🚀 Start Processing"
5. View results in "🗄️ Database Viewer"

### Use Case 2: Batch Processing

1. Upload multiple PCB images at once
2. Enable all processing options
3. Start processing
4. Monitor progress
5. Check "📊 Statistics" for overview

### Use Case 3: Extract Part Numbers

1. Upload PCB image with visible IC chips
2. Ensure "Extract MPNs (OCR)" is enabled
3. Process the image
4. Go to "🗄️ Database Viewer" → "📝 OCR Results"
5. View extracted part numbers

### Use Case 4: Review Processing History

1. Go to "🗄️ Database Viewer"
2. Select "🔄 Jobs Log"
3. Browse all processed jobs
4. Click a job to see details
5. View associated detections and results

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nuts_vision
DB_USER=nuts_user
DB_PASSWORD=nuts_password
```

### Streamlit Configuration

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = "localhost"
maxUploadSize = 200

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

---

## 🆘 Troubleshooting

### Database Not Connected

**Check if PostgreSQL is running:**
```bash
# Docker
docker-compose ps

# System
sudo systemctl status postgresql
```

**Test connection:**
```bash
psql -h localhost -U nuts_user -d nuts_vision
```

### Model Not Found

**Train the model first:**
```bash
python src/train.py --data data.yaml --epochs 100 --model-size n
```

**Or specify custom path in the web interface**

### Port Already in Use

**Use a different port:**
```bash
streamlit run app.py --server.port 8502
```

### Upload Fails

- Check file size (< 200 MB)
- Verify format (JPG, JPEG, PNG)
- Ensure `uploads/` directory has write permissions

---

## 📚 Next Steps

- **[INTERFACE_WEB.md](INTERFACE_WEB.md)** - Complete web interface documentation
- **[DATABASE.md](DATABASE.md)** - Database setup and queries
- **[README_FR.md](README_FR.md)** - French documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture

---

## 🎯 Key Benefits of Web Interface

✅ **No Command Line Required** - Point-and-click operation  
✅ **Visual Database Browser** - Supabase-like table viewer  
✅ **Real-time Progress** - Watch processing as it happens  
✅ **Interactive Statistics** - Charts and graphs  
✅ **Easy Image Upload** - Drag and drop interface  
✅ **Job History** - Track all processing operations  
✅ **Multi-image Support** - Process batches easily  

**Perfect for:**
- Non-technical users
- Quick prototyping
- Data exploration
- Result visualization
- Learning and demonstration
