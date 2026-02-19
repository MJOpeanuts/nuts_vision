#!/usr/bin/env python3
"""
Streamlit Web Interface for nuts_vision
Provides a graphical interface for:
- PCB image upload and component detection
- Per-job viewer (input photo, result photo, cropped components, metadata)
- Database viewer
- Statistics
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
    page_icon="\U0001f527",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    .dataframe { font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "db" not in st.session_state and DB_AVAILABLE:
    try:
        st.session_state.db = get_db_manager_from_env()
        st.session_state.db_connected = st.session_state.db.test_connection()
    except Exception as e:
        st.session_state.db_connected = False
        st.session_state.db_error = str(e)

# Sidebar
st.sidebar.markdown("## \U0001f527 nuts_vision")
st.sidebar.markdown("**Electronic Component Analyzer**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["\U0001f3e0 Home", "\U0001f4e4 Upload & Process", "\U0001f50d Job Viewer",
     "\U0001f5c4\ufe0f Database Viewer", "\U0001f4ca Statistics", "\u2139\ufe0f About"]
)

st.sidebar.markdown("---")
if DB_AVAILABLE:
    if st.session_state.get("db_connected", False):
        st.sidebar.success("\u2705 Database Connected")
    else:
        st.sidebar.error("\u274c Database Disconnected")
        if "db_error" in st.session_state:
            st.sidebar.text(f"Error: {st.session_state.db_error}")
else:
    st.sidebar.warning("\u26a0\ufe0f Database Module Not Available")


# ========== HOME PAGE ==========
if page == "\U0001f3e0 Home":
    st.markdown('<div class="main-header">\U0001f527 nuts_vision</div>', unsafe_allow_html=True)
    st.markdown("### Electronic Component Detection System")
    st.markdown("""
    Welcome to **nuts_vision** — an automated system for analyzing electronic circuit boards.

    #### \U0001f3af How it works:
    1. **Upload** a photo of an electronic circuit board
    2. **Detect** — YOLOv8 identifies and classifies every component
    3. **Crop** — each detected component is saved as a separate image
    4. **Browse** — all results are organized in a per-job folder

    #### \U0001f4cb Detectable Components:
    """)
    components = [
        "IC (Integrated Circuit)", "LED", "Battery", "Buzzer",
        "Capacitor", "Clock", "Connector", "Diode",
        "Display", "Fuse", "Inductor", "Potentiometer",
        "Relay", "Resistor", "Switch", "Transistor"
    ]
    cols = st.columns(4)
    for idx, comp in enumerate(components):
        cols[idx % 4].markdown(f"\u2713 {comp}")

    st.markdown("---")
    st.markdown("""
    #### \U0001f4c1 Output structure (per job):
    ```
    jobs/
      <image_name>_<date>_<time>/
        input.<ext>    — original photo
        result.jpg     — annotated photo with bounding boxes
        crops/         — one cropped image per detected component
        metadata.json  — detection data
    ```
    """)

    if st.session_state.get("db_connected", False):
        try:
            stats = st.session_state.db.get_detection_statistics()
            st.markdown("---")
            st.markdown("### \U0001f4ca Quick Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Images", stats.get("total_images", 0))
            with col2:
                st.metric("Total Jobs", stats.get("total_jobs", 0))
            with col3:
                st.metric("Detections", stats.get("total_detections", 0))
        except Exception as e:
            st.warning(f"Could not load statistics: {e}")


# ========== UPLOAD & PROCESS PAGE ==========
elif page == "\U0001f4e4 Upload & Process":
    st.markdown('<div class="main-header">\U0001f4e4 Upload & Process Images</div>', unsafe_allow_html=True)

    default_model_path = "runs/detect/component_detector/weights/best.pt"
    model_exists = Path(default_model_path).exists()

    if not model_exists:
        st.warning("""
        \u26a0\ufe0f **Model not found!**
        Train a model first:
        ```bash
        python src/train.py --data data.yaml --epochs 100 --model-size n
        ```
        Or specify a custom model path below.
        """)

    st.markdown("### Model Configuration")
    col1, col2 = st.columns([3, 1])
    with col1:
        model_path = st.text_input("Model Path", value=default_model_path if model_exists else "",
                                    help="Path to the trained YOLO model (best.pt)")
    with col2:
        conf_threshold = st.slider("Confidence Threshold", min_value=0.1, max_value=0.9,
                                    value=0.25, step=0.05)

    st.markdown("### Upload Images")
    uploaded_files = st.file_uploader("Choose PCB images", type=["jpg", "jpeg", "png"],
                                       accept_multiple_files=True)

    st.markdown("### Processing Options")
    use_database = st.checkbox("Log to Database", value=True)

    if st.button("\U0001f680 Start Processing", type="primary",
                 disabled=not uploaded_files or not model_path):
        if not Path(model_path).exists():
            st.error(f"Model file not found: {model_path}")
        else:
            upload_dir = Path("jobs") / "_uploads"
            upload_dir.mkdir(parents=True, exist_ok=True)
            progress_bar = st.progress(0)
            status_text = st.empty()
            try:
                status_text.text("Initializing pipeline...")
                pipeline = ComponentAnalysisPipeline(
                    model_path=model_path,
                    conf_threshold=conf_threshold,
                    use_database=use_database and st.session_state.get("db_connected", False)
                )
                total_files = len(uploaded_files)
                results_summary = []
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name} ({idx+1}/{total_files})...")
                    progress_bar.progress(idx / total_files)
                    file_path = upload_dir / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    try:
                        result = pipeline.process_image(str(file_path.resolve()), jobs_base_dir="jobs")
                        results_summary.append({
                            "file": uploaded_file.name,
                            "status": "\u2705 Success",
                            "job_folder": result["job_folder"],
                            "detections": result["metadata"]["total_detections"]
                        })
                    except Exception as e:
                        results_summary.append({
                            "file": uploaded_file.name,
                            "status": f"\u274c Error: {str(e)}",
                            "job_folder": "",
                            "detections": 0
                        })
                progress_bar.progress(1.0)
                status_text.text("Processing complete!")
                st.success("\u2705 Processing completed!")
                st.markdown("### Results Summary")
                st.dataframe(pd.DataFrame(results_summary), use_container_width=True)
                st.info("\U0001f4c1 View detailed results in the **Job Viewer** page.")
            except Exception as e:
                st.error(f"Error during processing: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

    if uploaded_files:
        st.markdown("---")
        st.markdown("### \U0001f4f7 Uploaded Images Preview")
        cols = st.columns(min(3, len(uploaded_files)))
        for idx, uploaded_file in enumerate(uploaded_files[:6]):
            with cols[idx % 3]:
                st.image(Image.open(uploaded_file), caption=uploaded_file.name, use_container_width=True)


# ========== JOB VIEWER PAGE ==========
elif page == "\U0001f50d Job Viewer":
    st.markdown('<div class="main-header">\U0001f50d Job Viewer</div>', unsafe_allow_html=True)
    st.markdown("Browse results: input photo, annotated result, cropped components, and metadata.")

    jobs_base = Path("jobs")
    job_folders = sorted(
        [d for d in jobs_base.iterdir() if d.is_dir() and (d / "metadata.json").exists()],
        key=lambda d: d.stat().st_mtime, reverse=True
    ) if jobs_base.exists() else []

    db_jobs = []
    if st.session_state.get("db_connected", False):
        try:
            db_jobs = st.session_state.db.get_all_jobs()
        except Exception:
            pass

    if not job_folders and not db_jobs:
        st.info("No jobs found yet. Upload and process a PCB image first!")
    else:
        fs_job_names = {d.name for d in job_folders}
        job_options = [d.name for d in job_folders]
        job_folder_map = {d.name: d for d in job_folders}
        for job in db_jobs:
            jname = job.get("job_name") or f"job_{job['job_id']}"
            if jname not in fs_job_names:
                job_options.append(f"{jname} (folder missing)")

        if not job_options:
            st.info("No jobs found.")
        else:
            selected_label = st.selectbox("Choose a job to inspect", job_options)
            selected_name = selected_label.replace(" (folder missing)", "")
            job_dir = job_folder_map.get(selected_name)

            if job_dir and job_dir.exists():
                with open(job_dir / "metadata.json") as f:
                    metadata = json.load(f)

                st.markdown("---")
                st.markdown("### \U0001f4cb Job Information")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Job Name", metadata.get("job_name", "—"))
                with col2:
                    st.metric("Total Detections", metadata.get("total_detections", 0))
                with col3:
                    date_str = metadata.get("date", "")
                    try:
                        dt = datetime.fromisoformat(date_str)
                        st.metric("Date", dt.strftime("%Y-%m-%d %H:%M:%S"))
                    except Exception:
                        st.metric("Date", date_str)
                st.text(f"Model: {metadata.get('model', '—')}")
                st.text(f"Folder: {job_dir}")

                st.markdown("---")
                st.markdown("### \U0001f4f8 Input Photo")
                input_photos = list(job_dir.glob("input.*"))
                if input_photos:
                    try:
                        st.image(Image.open(input_photos[0]), caption="Input", use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not display input photo: {e}")
                else:
                    st.warning("Input photo not found.")

                st.markdown("---")
                st.markdown("### \U0001f3af Result Photo (Annotated)")
                result_photo = job_dir / "result.jpg"
                if result_photo.exists():
                    try:
                        st.image(Image.open(result_photo), caption="Detected components", use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not display result photo: {e}")
                else:
                    st.warning("Result photo not found.")

                crops_dir = job_dir / "crops"
                crop_files = sorted(crops_dir.glob("*.jpg")) if crops_dir.exists() else []
                detections = metadata.get("detections", [])

                if crop_files:
                    st.markdown("---")
                    st.markdown(f"### \u2702\ufe0f Cropped Components ({len(crop_files)} total)")
                    det_by_file = {d.get("crop_file"): d for d in detections if d.get("crop_file")}
                    cols_per_row = 4
                    rows = [crop_files[i:i+cols_per_row] for i in range(0, len(crop_files), cols_per_row)]
                    for row in rows:
                        cols = st.columns(cols_per_row)
                        for col, crop_file in zip(cols, row):
                            with col:
                                try:
                                    det = det_by_file.get(crop_file.name, {})
                                    caption = det.get("class_name", crop_file.stem)
                                    if "confidence" in det:
                                        caption += f" ({det['confidence']:.2f})"
                                    st.image(Image.open(crop_file), caption=caption, use_container_width=True)
                                except Exception as e:
                                    st.error(f"Error: {e}")
                else:
                    st.info("No cropped components found.")

                st.markdown("---")
                st.markdown("### \U0001f4c4 Metadata")
                if detections:
                    df_det = pd.DataFrame([
                        {
                            "index": d["index"], "class": d["class_name"],
                            "confidence": d["confidence"],
                            "x1": round(d["bbox"][0], 1), "y1": round(d["bbox"][1], 1),
                            "x2": round(d["bbox"][2], 1), "y2": round(d["bbox"][3], 1),
                            "crop_file": d.get("crop_file", "—")
                        } for d in detections
                    ])
                    st.dataframe(df_det, use_container_width=True)
                else:
                    st.info("No detections in this job.")

                with st.expander("\U0001f4c4 Raw metadata.json"):
                    st.json(metadata)
            else:
                st.warning(f"Job folder not found on disk for: {selected_name}")


# ========== DATABASE VIEWER PAGE ==========
elif page == "\U0001f5c4\ufe0f Database Viewer":
    st.markdown('<div class="main-header">\U0001f5c4\ufe0f Database Viewer</div>', unsafe_allow_html=True)

    if not st.session_state.get("db_connected", False):
        st.error("""
        \u274c **Database not connected!**
        Start PostgreSQL:
        ```bash
        docker-compose up -d
        ```
        Environment variables: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
        """)
    else:
        table_view = st.selectbox("Select Table",
            ["\U0001f4f8 Images Input", "\U0001f504 Jobs Log",
             "\U0001f3af Detections", "\u2702\ufe0f Cropped Components"])

        if st.button("\U0001f504 Refresh"):
            st.rerun()

        try:
            if table_view == "\U0001f4f8 Images Input":
                data = st.session_state.db.get_all_images()
                if data:
                    df = pd.DataFrame(data)
                    if "upload_at" in df.columns:
                        df["upload_at"] = pd.to_datetime(df["upload_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                    st.dataframe(df, use_container_width=True, height=400)
                    st.caption(f"Total records: {len(df)}")
                else:
                    st.info("No images in database yet.")

            elif table_view == "\U0001f504 Jobs Log":
                data = st.session_state.db.get_all_jobs()
                if data:
                    df = pd.DataFrame(data)
                    for col in ["started_at", "ended_at"]:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d %H:%M:%S")
                    st.dataframe(df, use_container_width=True, height=400)
                    st.caption(f"Total records: {len(df)}")
                    if len(df) > 0:
                        st.markdown("---")
                        job_id = st.selectbox("Select Job ID", df["job_id"].tolist())
                        if job_id:
                            stats = st.session_state.db.get_job_statistics(job_id)
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Detections", stats.get("total_detections", 0))
                            with col2:
                                st.metric("Components Cropped", stats.get("total_crops", 0))
                else:
                    st.info("No jobs in database yet.")

            elif table_view == "\U0001f3af Detections":
                all_jobs = st.session_state.db.get_all_jobs()
                job_options = ["All Jobs"] + [f"Job {j['job_id']} - {j['file_name']}" for j in all_jobs]
                selected_job = st.selectbox("Filter by Job", job_options)
                job_id = None
                if selected_job != "All Jobs":
                    job_id = int(selected_job.split()[1])
                data = st.session_state.db.get_all_detections(job_id=job_id)
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True, height=400)
                    st.caption(f"Total records: {len(df)}")
                    if "class_name" in df.columns:
                        st.markdown("---")
                        st.bar_chart(df["class_name"].value_counts())
                else:
                    st.info("No detections in database yet.")

            elif table_view == "\u2702\ufe0f Cropped Components":
                with st.session_state.db.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT ic.*, d.class_name, j.job_id, j.job_name
                            FROM ics_cropped ic
                            JOIN detections d ON ic.detection_id = d.detection_id
                            JOIN log_jobs j ON ic.job_id = j.job_id
                            ORDER BY ic.created_at DESC LIMIT 100
                        """)
                        columns = [desc[0] for desc in cursor.description]
                        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                if data:
                    df = pd.DataFrame(data)
                    if "created_at" in df.columns:
                        df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                    st.dataframe(df, use_container_width=True, height=400)
                    st.caption(f"Total records: {len(df)}")
                else:
                    st.info("No cropped components in database yet.")

        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


# ========== STATISTICS PAGE ==========
elif page == "\U0001f4ca Statistics":
    st.markdown('<div class="main-header">\U0001f4ca Statistics & Analytics</div>', unsafe_allow_html=True)

    if not st.session_state.get("db_connected", False):
        st.warning("Database not connected. Statistics require database access.")
    else:
        try:
            stats = st.session_state.db.get_detection_statistics()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Images", stats.get("total_images", 0))
            with col2:
                st.metric("Total Jobs", stats.get("total_jobs", 0))
            with col3:
                st.metric("Total Detections", stats.get("total_detections", 0))

            st.markdown("---")
            component_counts = stats.get("component_counts", {})
            if component_counts:
                df_c = pd.DataFrame(list(component_counts.items()),
                                     columns=["Component", "Count"]).sort_values("Count", ascending=False)
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.bar_chart(df_c.set_index("Component"))
                with col2:
                    st.dataframe(df_c, use_container_width=True)
            else:
                st.info("No component data available yet.")

            st.markdown("---")
            recent_jobs = st.session_state.db.get_all_jobs(limit=10)
            if recent_jobs:
                df_j = pd.DataFrame(recent_jobs)
                for col in ["started_at", "ended_at"]:
                    if col in df_j.columns:
                        df_j[col] = pd.to_datetime(df_j[col]).dt.strftime("%Y-%m-%d %H:%M:%S")
                show_cols = [c for c in ["job_id", "job_name", "file_name", "started_at", "detection_count"]
                             if c in df_j.columns]
                st.dataframe(df_j[show_cols], use_container_width=True)
            else:
                st.info("No jobs recorded yet.")

        except Exception as e:
            st.error(f"Error: {str(e)}")


# ========== ABOUT PAGE ==========
elif page == "\u2139\ufe0f About":
    st.markdown('<div class="main-header">\u2139\ufe0f About nuts_vision</div>', unsafe_allow_html=True)
    st.markdown("""
    ### \U0001f527 Electronic Component Detection System

    **nuts_vision** analyses photos of electronic circuit boards, detects components,
    and produces cropped images of each detected component.

    #### \U0001f3af Key Technologies:
    - **YOLOv8**: object detection
    - **PostgreSQL** *(optional)*: logging
    - **Streamlit**: web interface
    - **OpenCV**: image processing

    #### \U0001f4c1 Job Folder Structure:
    ```
    jobs/
      <image_name>_<YYYYMMDD>_<HHMMSS>/
        input.<ext>    — original photo
        result.jpg     — annotated photo
        crops/         — one image per component
        metadata.json  — detection data
    ```

    **Version**: 2.0.0 | **License**: CC BY 4.0
    """)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Database Status:**")
        if st.session_state.get("db_connected", False):
            st.success("\u2705 Connected")
            st.text(f"Host: {os.getenv('DB_HOST', 'localhost')}")
            st.text(f"Port: {os.getenv('DB_PORT', '5432')}")
            st.text(f"Database: {os.getenv('DB_NAME', 'nuts_vision')}")
        else:
            st.error("\u274c Not Connected")
    with col2:
        st.markdown("**Environment:**")
        st.text(f"Python: {sys.version.split()[0]}")
        st.text(f"Streamlit: {st.__version__}")
        default_model = Path("runs/detect/component_detector/weights/best.pt")
        st.text("Model: \u2705 Found" if default_model.exists() else "Model: \u274c Not trained")
