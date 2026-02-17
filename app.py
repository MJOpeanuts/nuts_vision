#!/usr/bin/env python3
"""
Streamlit Web Interface for nuts_vision
Provides a graphical interface for:
- Image upload and processing
- Supabase-like database viewer
- Results visualization
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import modules
try:
    from database import get_db_manager_from_env
    from pipeline import ComponentAnalysisPipeline
    DB_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    DB_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="nuts_vision - Electronic Component Analyzer",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .dataframe {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state and DB_AVAILABLE:
    try:
        st.session_state.db = get_db_manager_from_env()
        st.session_state.db_connected = st.session_state.db.test_connection()
    except Exception as e:
        st.session_state.db_connected = False
        st.session_state.db_error = str(e)

# Sidebar navigation
st.sidebar.markdown("## 🔧 nuts_vision")
st.sidebar.markdown("**Electronic Component Analyzer**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📤 Upload & Process", "🗄️ Database Viewer", "📊 Statistics", "ℹ️ About"]
)

st.sidebar.markdown("---")

# Database status in sidebar
if DB_AVAILABLE:
    if st.session_state.get('db_connected', False):
        st.sidebar.success("✅ Database Connected")
    else:
        st.sidebar.error("❌ Database Disconnected")
        if 'db_error' in st.session_state:
            st.sidebar.text(f"Error: {st.session_state.db_error}")
else:
    st.sidebar.warning("⚠️ Database Module Not Available")


# ========== HOME PAGE ==========
if page == "🏠 Home":
    st.markdown('<div class="main-header">🔧 nuts_vision</div>', unsafe_allow_html=True)
    st.markdown("### Electronic Component Detection & OCR System")
    
    st.markdown("""
    Welcome to **nuts_vision** - an automated system for analyzing electronic circuit boards using computer vision.
    
    #### 🎯 Key Features:
    
    - **Component Detection**: Automatically detect 16 types of electronic components using YOLOv8
    - **Image Processing**: Advanced preprocessing for accurate component recognition
    - **OCR Extraction**: Extract manufacturer part numbers (MPNs) from IC components
    - **Database Tracking**: Complete tracing of all processing operations
    - **Visualization**: Generate statistics and visual analysis of results
    
    #### 📋 Detectable Components:
    """)
    
    components = [
        "IC (Integrated Circuit)", "LED", "Battery", "Buzzer",
        "Capacitor", "Clock", "Connector", "Diode",
        "Display", "Fuse", "Inductor", "Potentiometer",
        "Relay", "Resistor", "Switch", "Transistor"
    ]
    
    cols = st.columns(4)
    for idx, comp in enumerate(components):
        cols[idx % 4].markdown(f"✓ {comp}")
    
    st.markdown("---")
    
    st.markdown("""
    #### 🚀 Quick Start:
    
    1. **Upload & Process**: Upload PCB images and run detection
    2. **Database Viewer**: Browse all processing results in Supabase-like tables
    3. **Statistics**: View analytics and visualizations
    
    #### 📖 Navigation:
    - Use the sidebar to navigate between different sections
    - Check database connection status in the sidebar
    """)
    
    # Show quick stats if database is available
    if st.session_state.get('db_connected', False):
        try:
            stats = st.session_state.db.get_detection_statistics()
            
            st.markdown("---")
            st.markdown("### 📊 Quick Statistics")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Images", stats.get('total_images', 0))
            with col2:
                st.metric("Total Jobs", stats.get('total_jobs', 0))
            with col3:
                st.metric("Detections", stats.get('total_detections', 0))
            with col4:
                st.metric("OCR Results", stats.get('total_ocr_results', 0))
            with col5:
                st.metric("MPNs Extracted", stats.get('successful_mpn_extractions', 0))
            
        except Exception as e:
            st.warning(f"Could not load statistics: {e}")


# ========== UPLOAD & PROCESS PAGE ==========
elif page == "📤 Upload & Process":
    st.markdown('<div class="main-header">📤 Upload & Process Images</div>', unsafe_allow_html=True)
    
    # Check if model exists
    default_model_path = "runs/detect/component_detector/weights/best.pt"
    model_exists = Path(default_model_path).exists()
    
    if not model_exists:
        st.warning("""
        ⚠️ **Model not found!**
        
        The YOLO model hasn't been trained yet. Please train a model first:
        ```bash
        python src/train.py --data data.yaml --epochs 100 --model-size n
        ```
        
        Or specify a custom model path below.
        """)
    
    # Model configuration
    st.markdown("### Model Configuration")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        model_path = st.text_input(
            "Model Path",
            value=default_model_path if model_exists else "",
            help="Path to the trained YOLO model (best.pt)"
        )
    
    with col2:
        conf_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.1,
            max_value=0.9,
            value=0.25,
            step=0.05,
            help="Minimum confidence score for detections"
        )
    
    # Upload section
    st.markdown("### Upload Images")
    uploaded_files = st.file_uploader(
        "Choose PCB images",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Upload one or more images of electronic circuit boards"
    )
    
    # Processing options
    st.markdown("### Processing Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        extract_mpn = st.checkbox("Extract MPNs (OCR)", value=True, help="Run OCR to extract part numbers from ICs")
    with col2:
        use_database = st.checkbox("Log to Database", value=True, help="Save results to database")
    with col3:
        create_viz = st.checkbox("Create Visualizations", value=True, help="Generate charts and graphs")
    
    # Process button
    if st.button("🚀 Start Processing", type="primary", disabled=not uploaded_files or not model_path):
        if not Path(model_path).exists():
            st.error(f"Model file not found: {model_path}")
        else:
            # Create temp directory for uploads
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Initialize pipeline
                status_text.text("Initializing pipeline...")
                pipeline = ComponentAnalysisPipeline(
                    model_path=model_path,
                    conf_threshold=conf_threshold,
                    use_database=use_database and st.session_state.get('db_connected', False)
                )
                
                # Process each uploaded file
                total_files = len(uploaded_files)
                results_summary = []
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name} ({idx+1}/{total_files})...")
                    progress_bar.progress((idx) / total_files)
                    
                    # Save uploaded file
                    file_path = upload_dir / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Run pipeline
                    try:
                        pipeline.run_pipeline(
                            image_path=str(file_path),
                            extract_mpn=extract_mpn,
                            create_visualizations=create_viz
                        )
                        results_summary.append({
                            'file': uploaded_file.name,
                            'status': '✅ Success',
                            'path': str(file_path)
                        })
                    except Exception as e:
                        results_summary.append({
                            'file': uploaded_file.name,
                            'status': f'❌ Error: {str(e)}',
                            'path': str(file_path)
                        })
                
                progress_bar.progress(1.0)
                status_text.text("Processing complete!")
                
                # Show results
                st.success("✅ Processing completed!")
                
                st.markdown("### Results Summary")
                df_results = pd.DataFrame(results_summary)
                st.dataframe(df_results, use_container_width=True)
                
                # Show output location
                st.info("""
                📁 **Output Location**: `outputs/`
                - Detection results: `outputs/results/`
                - Cropped components: `outputs/cropped_components/`
                - Visualizations: `outputs/visualizations/`
                """)
                
            except Exception as e:
                st.error(f"Error during processing: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # Show upload preview
    if uploaded_files:
        st.markdown("---")
        st.markdown("### 📷 Uploaded Images Preview")
        
        cols = st.columns(min(3, len(uploaded_files)))
        for idx, uploaded_file in enumerate(uploaded_files[:6]):  # Show max 6 previews
            with cols[idx % 3]:
                image = Image.open(uploaded_file)
                st.image(image, caption=uploaded_file.name, use_container_width=True)


# ========== DATABASE VIEWER PAGE ==========
elif page == "🗄️ Database Viewer":
    st.markdown('<div class="main-header">🗄️ Database Viewer</div>', unsafe_allow_html=True)
    st.markdown("### Supabase-like Database Interface")
    
    if not st.session_state.get('db_connected', False):
        st.error("""
        ❌ **Database not connected!**
        
        Please ensure PostgreSQL is running and properly configured.
        
        **Quick Start with Docker:**
        ```bash
        docker-compose up -d
        ```
        
        **Environment Variables:**
        - DB_HOST (default: localhost)
        - DB_PORT (default: 5432)
        - DB_NAME (default: nuts_vision)
        - DB_USER (default: nuts_user)
        - DB_PASSWORD (default: nuts_password)
        """)
    else:
        # Table selector
        table_view = st.selectbox(
            "Select Table",
            ["📸 Images Input", "🔄 Jobs Log", "🎯 Detections", "✂️ Cropped ICs", "📝 OCR Results"]
        )
        
        # Refresh button
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        try:
            # Display selected table
            if table_view == "📸 Images Input":
                st.markdown("### Images Input Table")
                st.markdown("*All uploaded/processed images*")
                
                data = st.session_state.db.get_all_images()
                if data:
                    df = pd.DataFrame(data)
                    # Format timestamps
                    if 'upload_at' in df.columns:
                        df['upload_at'] = pd.to_datetime(df['upload_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    st.dataframe(df, use_container_width=True, height=400)
                    st.caption(f"Total records: {len(df)}")
                else:
                    st.info("No images in database yet.")
            
            elif table_view == "🔄 Jobs Log":
                st.markdown("### Jobs Log Table")
                st.markdown("*All detection jobs and their status*")
                
                data = st.session_state.db.get_all_jobs()
                if data:
                    df = pd.DataFrame(data)
                    # Format timestamps
                    for col in ['started_at', 'ended_at']:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    st.dataframe(df, use_container_width=True, height=400)
                    st.caption(f"Total records: {len(df)}")
                    
                    # Show job details
                    if len(df) > 0:
                        st.markdown("---")
                        st.markdown("### Job Details")
                        job_id = st.selectbox("Select Job ID to view details", df['job_id'].tolist())
                        
                        if job_id:
                            stats = st.session_state.db.get_job_statistics(job_id)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Detections", stats.get('total_detections', 0))
                            with col2:
                                st.metric("ICs Cropped", stats.get('total_ics_cropped', 0))
                            with col3:
                                st.metric("OCR Results", stats.get('total_ocr_results', 0))
                else:
                    st.info("No jobs in database yet.")
            
            elif table_view == "🎯 Detections":
                st.markdown("### Detections Table")
                st.markdown("*All component detections with bounding boxes*")
                
                # Optional filter by job
                all_jobs = st.session_state.db.get_all_jobs()
                if all_jobs:
                    job_options = ["All Jobs"] + [f"Job {j['job_id']} - {j['file_name']}" for j in all_jobs]
                    selected_job = st.selectbox("Filter by Job", job_options)
                    
                    job_id = None
                    if selected_job != "All Jobs":
                        job_id = int(selected_job.split()[1])
                    
                    data = st.session_state.db.get_all_detections(job_id=job_id)
                else:
                    data = st.session_state.db.get_all_detections()
                
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True, height=400)
                    st.caption(f"Total records: {len(df)}")
                    
                    # Component type distribution
                    if 'class_name' in df.columns:
                        st.markdown("---")
                        st.markdown("### Component Distribution")
                        component_counts = df['class_name'].value_counts()
                        st.bar_chart(component_counts)
                else:
                    st.info("No detections in database yet.")
            
            elif table_view == "✂️ Cropped ICs":
                st.markdown("### Cropped ICs Table")
                st.markdown("*All cropped IC component images*")
                
                # Query database
                with st.session_state.db.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT 
                                ic.*,
                                d.class_name,
                                j.job_id
                            FROM ics_cropped ic
                            JOIN detections d ON ic.detection_id = d.detection_id
                            JOIN log_jobs j ON ic.job_id = j.job_id
                            ORDER BY ic.created_at DESC
                            LIMIT 100
                        """)
                        columns = [desc[0] for desc in cursor.description]
                        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                if data:
                    df = pd.DataFrame(data)
                    if 'created_at' in df.columns:
                        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    st.dataframe(df, use_container_width=True, height=400)
                    st.caption(f"Total records: {len(df)}")
                else:
                    st.info("No cropped ICs in database yet.")
            
            elif table_view == "📝 OCR Results":
                st.markdown("### OCR Results Table")
                st.markdown("*All OCR extractions with MPNs*")
                
                data = st.session_state.db.get_all_ocr_results()
                
                if data:
                    df = pd.DataFrame(data)
                    if 'processed_at' in df.columns:
                        df['processed_at'] = pd.to_datetime(df['processed_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    st.dataframe(df, use_container_width=True, height=400)
                    st.caption(f"Total records: {len(df)}")
                    
                    # Show success rate
                    if 'cleaned_mpn' in df.columns:
                        successful = df[df['cleaned_mpn'].notna() & (df['cleaned_mpn'] != '')].shape[0]
                        total = len(df)
                        success_rate = (successful / total * 100) if total > 0 else 0
                        
                        st.markdown("---")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total OCR Attempts", total)
                        with col2:
                            st.metric("Successful Extractions", successful)
                        with col3:
                            st.metric("Success Rate", f"{success_rate:.1f}%")
                else:
                    st.info("No OCR results in database yet.")
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


# ========== STATISTICS PAGE ==========
elif page == "📊 Statistics":
    st.markdown('<div class="main-header">📊 Statistics & Analytics</div>', unsafe_allow_html=True)
    
    if not st.session_state.get('db_connected', False):
        st.warning("Database not connected. Statistics require database access.")
    else:
        try:
            stats = st.session_state.db.get_detection_statistics()
            
            # Overview metrics
            st.markdown("### 📈 Overview")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Images", stats.get('total_images', 0))
            with col2:
                st.metric("Total Jobs", stats.get('total_jobs', 0))
            with col3:
                st.metric("Total Detections", stats.get('total_detections', 0))
            with col4:
                st.metric("OCR Results", stats.get('total_ocr_results', 0))
            with col5:
                mpn_success = stats.get('successful_mpn_extractions', 0)
                total_ocr = stats.get('total_ocr_results', 1)
                success_rate = (mpn_success / total_ocr * 100) if total_ocr > 0 else 0
                st.metric("MPN Success Rate", f"{success_rate:.1f}%")
            
            # Component distribution
            st.markdown("---")
            st.markdown("### 🔧 Component Distribution")
            
            component_counts = stats.get('component_counts', {})
            if component_counts:
                df_components = pd.DataFrame(
                    list(component_counts.items()),
                    columns=['Component', 'Count']
                ).sort_values('Count', ascending=False)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.bar_chart(df_components.set_index('Component'))
                
                with col2:
                    st.dataframe(df_components, use_container_width=True, height=400)
            else:
                st.info("No component data available yet.")
            
            # Recent jobs
            st.markdown("---")
            st.markdown("### 🕐 Recent Jobs")
            
            recent_jobs = st.session_state.db.get_all_jobs(limit=10)
            if recent_jobs:
                df_jobs = pd.DataFrame(recent_jobs)
                
                # Format timestamps
                for col in ['started_at', 'ended_at']:
                    if col in df_jobs.columns:
                        df_jobs[col] = pd.to_datetime(df_jobs[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                st.dataframe(
                    df_jobs[['job_id', 'file_name', 'started_at', 'detection_count']],
                    use_container_width=True
                )
            else:
                st.info("No jobs recorded yet.")
            
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")


# ========== ABOUT PAGE ==========
elif page == "ℹ️ About":
    st.markdown('<div class="main-header">ℹ️ About nuts_vision</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🔧 Electronic Component Detection & OCR System
    
    **nuts_vision** is an automated computer vision system designed to analyze electronic circuit boards,
    detect components, and extract manufacturer part numbers.
    
    #### 🎯 Key Technologies:
    
    - **YOLOv8**: State-of-the-art object detection for component identification
    - **Tesseract OCR**: Text extraction from IC components
    - **PostgreSQL**: Complete tracing and logging of all operations
    - **Streamlit**: Modern, interactive web interface
    - **OpenCV**: Advanced image processing and manipulation
    
    #### 📊 Database Schema:
    
    - `images_input`: Uploaded images tracking
    - `log_jobs`: Detection job execution logs
    - `detections`: Component detection results with bounding boxes
    - `ics_cropped`: Cropped IC images for OCR processing
    - `ics_ocr`: OCR results with extracted MPNs
    
    #### 🚀 Workflow:
    
    1. **Upload**: Upload PCB images through the web interface
    2. **Detection**: YOLO model detects and classifies components
    3. **Cropping**: Detected ICs are cropped for OCR processing
    4. **OCR**: Tesseract extracts manufacturer part numbers
    5. **Database**: All results are logged to PostgreSQL
    6. **Visualization**: View results and statistics
    
    #### 📖 Documentation:
    
    - [README.md](README.md) - English documentation
    - [README_FR.md](README_FR.md) - French documentation
    - [DATABASE.md](DATABASE.md) - Database setup guide
    - [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
    
    #### 🤝 Contributing:
    
    Contributions are welcome! Please check the GitHub repository for more information.
    
    ---
    
    **Version**: 1.0.0  
    **License**: CC BY 4.0  
    **Repository**: [github.com/MJOpeanuts/nuts_vision](https://github.com/MJOpeanuts/nuts_vision)
    """)
    
    # System information
    st.markdown("---")
    st.markdown("### 💻 System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Database Status:**")
        if st.session_state.get('db_connected', False):
            st.success("✅ Connected")
            st.text(f"Host: {os.getenv('DB_HOST', 'localhost')}")
            st.text(f"Port: {os.getenv('DB_PORT', '5432')}")
            st.text(f"Database: {os.getenv('DB_NAME', 'nuts_vision')}")
        else:
            st.error("❌ Not Connected")
    
    with col2:
        st.markdown("**Environment:**")
        st.text(f"Python: {sys.version.split()[0]}")
        st.text(f"Streamlit: {st.__version__}")
        
        # Check for model
        default_model = Path("runs/detect/component_detector/weights/best.pt")
        if default_model.exists():
            st.text("Model: ✅ Found")
        else:
            st.text("Model: ❌ Not trained")
