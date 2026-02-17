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
    from psycopg2.extras import RealDictCursor
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
    ["🏠 Home", "📤 Upload & Process", "📷 Camera Control", "🔍 Job Viewer", "🗄️ Database Viewer", "📊 Statistics", "ℹ️ About"]
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
            # Create persistent directory for uploaded images
            # Store in outputs/images_input so they persist with other outputs
            upload_dir = Path("outputs") / "images_input"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
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
                    
                    # Save uploaded file to persistent location with absolute path
                    file_path = upload_dir / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Convert to absolute path for storage
                    absolute_file_path = file_path.resolve()
                    
                    # Run pipeline with absolute path
                    try:
                        pipeline.run_pipeline(
                            image_path=str(absolute_file_path),
                            extract_mpn=extract_mpn,
                            create_visualizations=create_viz
                        )
                        results_summary.append({
                            'file': uploaded_file.name,
                            'status': '✅ Success',
                            'path': str(absolute_file_path)
                        })
                    except Exception as e:
                        results_summary.append({
                            'file': uploaded_file.name,
                            'status': f'❌ Error: {str(e)}',
                            'path': str(absolute_file_path)
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
                - Uploaded images: `outputs/images_input/`
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


# ========== JOB VIEWER PAGE ==========
elif page == "🔍 Job Viewer":
    st.markdown('<div class="main-header">🔍 Job Viewer</div>', unsafe_allow_html=True)
    st.markdown("### View Saved Jobs with Images and OCR Results")
    
    if not st.session_state.get('db_connected', False):
        st.error("""
        ❌ **Database not connected!**
        
        Please ensure PostgreSQL is running and properly configured.
        
        **Quick Start with Docker:**
        ```bash
        docker-compose up -d
        ```
        """)
    else:
        try:
            # Get all jobs
            all_jobs = st.session_state.db.get_all_jobs()
            
            if not all_jobs:
                st.info("No jobs found in database. Process some images first!")
            else:
                # Job selector
                st.markdown("### Select a Job")
                
                # Create a more readable job list
                job_options = []
                job_mapping = {}
                for job in all_jobs:
                    job_display_text = f"Job {job['job_id']} - {job['file_name']} ({job['detection_count']} detections)"
                    job_options.append(job_display_text)
                    job_mapping[job_display_text] = job
                
                selected_job_label = st.selectbox(
                    "Choose a job to view details",
                    job_options,
                    help="Select a job to view its original image, cropped components, and OCR results"
                )
                
                if selected_job_label:
                    selected_job = job_mapping[selected_job_label]
                    job_id = selected_job['job_id']
                    
                    # Display job information
                    st.markdown("---")
                    st.markdown("### 📋 Job Information")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Job ID", job_id)
                    with col2:
                        st.metric("Detections", selected_job['detection_count'])
                    with col3:
                        started = pd.to_datetime(selected_job['started_at']).strftime('%Y-%m-%d %H:%M:%S')
                        st.metric("Started", started)
                    with col4:
                        if selected_job['ended_at']:
                            ended = pd.to_datetime(selected_job['ended_at']).strftime('%Y-%m-%d %H:%M:%S')
                            st.metric("Ended", ended)
                        else:
                            st.metric("Status", "Running")
                    
                    # Display original image
                    st.markdown("---")
                    st.markdown("### 📸 Original Image")
                    
                    original_image_path = selected_job['file_path']
                    if os.path.exists(original_image_path):
                        try:
                            original_image = Image.open(original_image_path)
                            st.image(original_image, caption=f"Original: {selected_job['file_name']}", use_container_width=True)
                        except Exception as e:
                            st.error(f"Error loading original image: {e}")
                    else:
                        st.warning(f"Original image not found at: {original_image_path}")
                    
                    # Get cropped ICs and OCR results for this job
                    with st.session_state.db.get_connection() as conn:
                        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                            cursor.execute("""
                                SELECT 
                                    ic.cropped_id,
                                    ic.cropped_file_path,
                                    ic.created_at,
                                    d.class_name,
                                    d.confidence,
                                    d.bbox_x1,
                                    d.bbox_y1,
                                    d.bbox_x2,
                                    d.bbox_y2,
                                    o.ocr_id,
                                    o.raw_text,
                                    o.cleaned_mpn,
                                    o.rotation_angle,
                                    o.processed_at
                                FROM ics_cropped ic
                                JOIN detections d ON ic.detection_id = d.detection_id
                                LEFT JOIN ics_ocr o ON ic.cropped_id = o.cropped_id
                                WHERE ic.job_id = %s
                                ORDER BY ic.cropped_id
                            """, (job_id,))
                            ic_components = [dict(row) for row in cursor.fetchall()]
                    
                    # Display cropped ICs and OCR results
                    if ic_components:
                        st.markdown("---")
                        st.markdown(f"### ✂️ Cropped IC Components ({len(ic_components)} total)")
                        
                        # Display in a grid
                        for idx, ic in enumerate(ic_components, 1):
                            with st.expander(f"🔍 IC #{idx} - {ic['class_name']} (Confidence: {ic['confidence']:.2f})", expanded=(idx == 1)):
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    # Display cropped image
                                    cropped_path = ic['cropped_file_path']
                                    if os.path.exists(cropped_path):
                                        try:
                                            cropped_img = Image.open(cropped_path)
                                            st.image(cropped_img, caption=f"Cropped IC #{idx}", use_container_width=True)
                                        except Exception as e:
                                            st.error(f"Error loading cropped image: {e}")
                                    else:
                                        st.warning(f"Cropped image not found")
                                    
                                    # Show bounding box info
                                    st.markdown("**Bounding Box:**")
                                    st.text(f"X1: {ic['bbox_x1']:.1f}, Y1: {ic['bbox_y1']:.1f}")
                                    st.text(f"X2: {ic['bbox_x2']:.1f}, Y2: {ic['bbox_y2']:.1f}")
                                
                                with col2:
                                    # Display OCR results
                                    st.markdown("**OCR Results:**")
                                    
                                    if ic['ocr_id']:
                                        # MPN (cleaned)
                                        if ic['cleaned_mpn']:
                                            st.success(f"**MPN:** {ic['cleaned_mpn']}")
                                        else:
                                            st.warning("**MPN:** Not extracted")
                                        
                                        # Raw text
                                        if ic['raw_text']:
                                            st.markdown("**Raw OCR Text:**")
                                            st.code(ic['raw_text'], language=None)
                                        else:
                                            st.info("No text detected")
                                        
                                        # Rotation angle
                                        if ic['rotation_angle'] is not None:
                                            st.text(f"Rotation: {ic['rotation_angle']}°")
                                        
                                        # Processing time
                                        if ic['processed_at']:
                                            processed_time = pd.to_datetime(ic['processed_at']).strftime('%Y-%m-%d %H:%M:%S')
                                            st.text(f"Processed: {processed_time}")
                                    else:
                                        st.info("No OCR results available for this component")
                                    
                                    # File path
                                    st.markdown("**File Path:**")
                                    st.text(cropped_path)
                        
                        # Summary statistics
                        st.markdown("---")
                        st.markdown("### 📊 Summary")
                        
                        total_ics = len(ic_components)
                        with_ocr = sum(1 for ic in ic_components if ic['ocr_id'] is not None)
                        with_mpn = sum(1 for ic in ic_components if ic['cleaned_mpn'])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total ICs", total_ics)
                        with col2:
                            st.metric("OCR Processed", with_ocr)
                        with col3:
                            st.metric("MPNs Extracted", with_mpn)
                            if with_ocr > 0:
                                success_rate = (with_mpn / with_ocr) * 100
                                st.caption(f"Success Rate: {success_rate:.1f}%")
                    else:
                        st.info("No cropped IC components found for this job.")
                        
        except Exception as e:
            st.error(f"Error loading job data: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


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


# ========== CAMERA CONTROL PAGE ==========
elif page == "📷 Camera Control":
    st.markdown('<div class="main-header">📷 Arducam 108MP Camera Control</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Control your Arducam 108MP Motorized Focus USB 3.0 Camera to capture high-quality images
    for component analysis.
    
    **Features:**
    - Connect to Arducam 108MP camera
    - Adjust motorized focus (manual or auto)
    - Capture high-resolution photos
    - Process captured photos with existing pipeline
    """)
    
    st.markdown("---")
    
    # Import camera control
    try:
        from camera_control import ArducamCamera
        camera_available = True
    except ImportError as e:
        st.error(f"Camera control module not available: {e}")
        camera_available = False
    
    if not camera_available:
        st.stop()
    
    # Initialize session state for camera
    if 'camera' not in st.session_state:
        st.session_state.camera = None
        st.session_state.camera_connected = False
        st.session_state.preview_running = False
    
    # Camera Connection Section
    st.markdown('<div class="sub-header">🔌 Camera Connection</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        camera_index = st.number_input("Camera Index", min_value=0, max_value=10, value=0, 
                                       help="Device index for the camera (usually 0)")
        
        # Resolution presets
        resolution_presets = {
            "HD (1280x720) - Fast Preview": (1280, 720, 30),
            "Full HD (1920x1080) - Recommended": (1920, 1080, 30),
            "2K (2560x1440) - High Quality": (2560, 1440, 15),
            "4K (3840x2160) - Max Quality": (3840, 2160, 10),
            "VGA (640x480) - Low Quality": (640, 480, 30),
            "Custom": None
        }
        
        selected_preset = st.selectbox(
            "Resolution Preset",
            list(resolution_presets.keys()),
            index=1,  # Default to Full HD
            help="Choose a preset or select Custom to specify your own resolution"
        )
        
        if resolution_presets[selected_preset] is None:  # Custom
            col_w, col_h, col_f = st.columns(3)
            with col_w:
                width = st.number_input("Width", min_value=640, max_value=7680, value=1920, step=64)
            with col_h:
                height = st.number_input("Height", min_value=480, max_value=4320, value=1080, step=64)
            with col_f:
                fps = st.selectbox("FPS", [10, 15, 20, 30, 60], index=3)
        else:
            width, height, fps = resolution_presets[selected_preset]
            st.info(f"📐 Resolution: {width}x{height} @ {fps}fps")
    
    with col2:
        st.markdown("**Status:**")
        if st.session_state.camera_connected:
            st.success("✅ Connected")
            # Display current camera info
            if st.session_state.camera:
                info = st.session_state.camera.get_camera_info()
                if info.get('connected'):
                    st.markdown(f"**Resolution:** {info['width']}x{info['height']}")
                    st.markdown(f"**FPS:** {info['fps']}")
                    st.markdown(f"**Focus:** {info['focus']}")
        else:
            st.warning("⚠️ Not Connected")
    
    # Connection buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔌 Connect", disabled=st.session_state.camera_connected):
            with st.spinner("Connecting to camera..."):
                st.session_state.camera = ArducamCamera(camera_index=camera_index)
                success = st.session_state.camera.connect(width=width, height=height, fps=fps)
                
                if success:
                    st.session_state.camera_connected = True
                    st.success("Camera connected successfully!")
                    st.rerun()
                else:
                    st.error("Failed to connect to camera. Please check the camera is plugged in and the index is correct.")
                    st.session_state.camera = None
    
    with col_btn2:
        if st.button("🔄 Disconnect", disabled=not st.session_state.camera_connected):
            if st.session_state.camera:
                st.session_state.camera.disconnect()
                st.session_state.camera = None
                st.session_state.camera_connected = False
                st.session_state.preview_running = False
                st.success("Camera disconnected")
                st.rerun()
    
    with col_btn3:
        if st.button("ℹ️ Camera Info", disabled=not st.session_state.camera_connected):
            if st.session_state.camera:
                info = st.session_state.camera.get_camera_info()
                st.json(info)
    
    st.markdown("---")
    
    # Only show controls if camera is connected
    if st.session_state.camera_connected and st.session_state.camera:
        
        # Focus Control Section
        st.markdown('<div class="sub-header">🎯 Focus Control</div>', unsafe_allow_html=True)
        
        st.markdown("""
        Adjust the camera focus manually using the slider below, or use auto-focus to automatically 
        find the optimal focus value. **Tip:** Enable live preview above to see focus changes in real-time!
        """)
        
        col_focus1, col_focus2 = st.columns([3, 1])
        
        with col_focus1:
            # Focus slider
            current_focus = st.session_state.camera.get_focus()
            if current_focus is None:
                current_focus = 0
            
            focus_value = st.slider("Focus Value", min_value=0, max_value=255, 
                                    value=int(current_focus), step=1,
                                    help="Adjust the motorized focus (0 = near, 255 = far)")
            
            # Auto-apply focus when slider changes
            if focus_value != int(current_focus):
                st.session_state.camera.set_focus(focus_value)
                if not st.session_state.live_preview_active:
                    st.info(f"Focus set to {focus_value}. Enable live preview to see the effect in real-time!")
        
        with col_focus2:
            st.markdown("**Auto Focus**")
            if st.button("🔍 Auto Focus Scan"):
                with st.spinner("Scanning for optimal focus... This may take 15-30 seconds"):
                    # Temporarily disable live preview during auto-focus
                    was_live = st.session_state.live_preview_active
                    st.session_state.live_preview_active = False
                    
                    # Perform auto-focus
                    best_focus, sharpness = st.session_state.camera.auto_focus_scan(
                        start=0, end=255, step=20
                    )
                    
                    st.success(f"✅ Optimal focus: {best_focus} (sharpness: {sharpness:.2f})")
                    
                    # Restore live preview state
                    st.session_state.live_preview_active = was_live
                    
                    # Trigger a rerun to update the slider
                    st.rerun()
            
            st.markdown("**Focus Presets**")
            col_near, col_mid, col_far = st.columns(3)
            with col_near:
                if st.button("📍 Near", help="Focus for close objects (~10cm)"):
                    st.session_state.camera.set_focus(50)
                    st.rerun()
            with col_mid:
                if st.button("📍 Mid", help="Focus for medium distance (~20cm)"):
                    st.session_state.camera.set_focus(125)
                    st.rerun()
            with col_far:
                if st.button("📍 Far", help="Focus for distant objects (~30cm+)"):
                    st.session_state.camera.set_focus(200)
                    st.rerun()
        
        st.markdown("---")
        
        # Preview Section
        st.markdown('<div class="sub-header">👁️ Live Preview</div>', unsafe_allow_html=True)
        
        st.markdown("""
        Use live preview to adjust focus in real-time. The preview will continuously update 
        to show the current camera view, making it easier to find the optimal focus setting.
        """)
        
        # Initialize preview state
        if 'live_preview_active' not in st.session_state:
            st.session_state.live_preview_active = False
        
        col_prev_ctrl, col_prev_status = st.columns([1, 3])
        
        with col_prev_ctrl:
            # Toggle live preview
            if st.button("▶️ Start Live Preview" if not st.session_state.live_preview_active else "⏸️ Stop Live Preview"):
                st.session_state.live_preview_active = not st.session_state.live_preview_active
                st.rerun()
            
            # Single frame capture
            if st.button("📸 Capture Single Frame"):
                st.session_state.capture_single_frame = True
            
            # Refresh rate control
            if st.session_state.live_preview_active:
                refresh_rate = st.select_slider(
                    "Refresh Rate",
                    options=[0.1, 0.3, 0.5, 1.0, 2.0],
                    value=st.session_state.preview_refresh_rate,
                    format_func=lambda x: f"{x}s ({1/x:.1f} FPS)" if x > 0 else "Max",
                    help="Control how often the preview updates (lower = faster but more CPU)"
                )
                if refresh_rate != st.session_state.preview_refresh_rate:
                    st.session_state.preview_refresh_rate = refresh_rate
        
        with col_prev_status:
            if st.session_state.live_preview_active:
                st.info("🔴 Live preview is running. Adjust focus slider below to see changes in real-time.")
            else:
                st.info("⚪ Live preview is stopped. Click 'Start Live Preview' to begin.")
        
        # Preview display area
        preview_placeholder = st.empty()
        
        # Refresh rate control for live preview
        if 'preview_refresh_rate' not in st.session_state:
            st.session_state.preview_refresh_rate = 0.5  # seconds
        
        # Live preview loop
        if st.session_state.live_preview_active:
            import time
            frame = st.session_state.camera.capture_frame()
            if frame is not None:
                # Convert BGR to RGB for display
                import cv2
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Calculate sharpness for focus feedback
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                preview_placeholder.image(
                    frame_rgb, 
                    caption=f"Live Preview - Sharpness: {sharpness:.2f} (higher is sharper)",
                    use_container_width=True
                )
                
                # Configurable refresh delay to control CPU/network usage
                time.sleep(st.session_state.preview_refresh_rate)
                st.rerun()
            else:
                st.error("Failed to capture frame from camera")
                st.session_state.live_preview_active = False
        elif st.session_state.get('capture_single_frame', False):
            # Capture and display single frame
            frame = st.session_state.camera.capture_frame()
            if frame is not None:
                import cv2
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Calculate sharpness
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                preview_placeholder.image(
                    frame_rgb, 
                    caption=f"Single Frame - Sharpness: {sharpness:.2f}",
                    use_container_width=True
                )
            st.session_state.capture_single_frame = False
        
        st.markdown("---")
        
        # Photo Capture Section
        st.markdown('<div class="sub-header">📸 Capture Photo</div>', unsafe_allow_html=True)
        
        col_cap1, col_cap2 = st.columns([2, 1])
        
        with col_cap1:
            quality = st.slider("JPEG Quality", min_value=50, max_value=100, value=95, step=5,
                               help="JPEG compression quality (higher = better quality, larger file)")
            
            custom_path = st.text_input("Custom Save Path (optional)", 
                                       placeholder="Leave empty for auto-generated path")
        
        with col_cap2:
            st.markdown("**Actions**")
            
            if st.button("📸 Capture Photo", type="primary"):
                with st.spinner("Capturing photo..."):
                    output_path = custom_path if custom_path else None
                    saved_path = st.session_state.camera.capture_photo(
                        output_path=output_path,
                        quality=quality
                    )
                    
                    if saved_path:
                        st.success(f"Photo saved to: {saved_path}")
                        
                        # Store in session state for processing
                        st.session_state.last_captured_photo = saved_path
                        
                        # Display the captured photo
                        try:
                            img = Image.open(saved_path)
                            st.image(img, caption=f"Captured: {Path(saved_path).name}", 
                                   use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not display image: {e}")
                    else:
                        st.error("Failed to capture photo")
        
        # Process Captured Photo Section
        if 'last_captured_photo' in st.session_state:
            st.markdown("---")
            st.markdown('<div class="sub-header">🔄 Process Captured Photo</div>', unsafe_allow_html=True)
            
            st.info(f"**Last captured photo:** {st.session_state.last_captured_photo}")
            
            col_proc1, col_proc2 = st.columns([2, 1])
            
            with col_proc1:
                st.markdown("""
                Process the captured photo through the nuts_vision pipeline to detect components
                and extract manufacturer part numbers.
                """)
            
            with col_proc2:
                if st.button("🔄 Process Image", type="primary"):
                    # Check if model exists
                    default_model_path = "runs/detect/component_detector/weights/best.pt"
                    
                    if not Path(default_model_path).exists():
                        st.error("Model not found. Please train a model first.")
                    else:
                        with st.spinner("Processing image through pipeline..."):
                            try:
                                # Import pipeline
                                from pipeline import ComponentAnalysisPipeline
                                
                                # Initialize pipeline
                                use_db = st.session_state.get('db_connected', False)
                                pipeline = ComponentAnalysisPipeline(
                                    model_path=default_model_path,
                                    use_database=use_db
                                )
                                
                                # Process the image
                                results = pipeline.process_image(st.session_state.last_captured_photo)
                                
                                st.success("✅ Image processed successfully!")
                                
                                # Display results
                                if results:
                                    st.markdown("**Results:**")
                                    st.json(results)
                                    
                                    # Link to Job Viewer
                                    st.info("📊 View detailed results in the **Job Viewer** page")
                                
                            except Exception as e:
                                st.error(f"Error processing image: {e}")
                                import traceback
                                st.code(traceback.format_exc())
    
    else:
        st.info("👆 Please connect to the camera first to access controls and capture photos.")


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
