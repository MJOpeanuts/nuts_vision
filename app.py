#!/usr/bin/env python3
"""
Streamlit Web Interface for nuts_vision
Provides a graphical interface for:
- PCB image upload and component detection
- PCBA Photo Booth (dual-model detection pipeline)
- Per-job viewer (input photo, result photo, cropped components, metadata)
- Database viewer
- Statistics
"""

import io
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont
import json
import numpy as np

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

try:
    from detect import DualModelDetector
    DUAL_DETECTOR_AVAILABLE = True
except ImportError:
    DUAL_DETECTOR_AVAILABLE = False

# All 16 component classes for comp_detect_best_v2
COMP_DETECT_CLASSES = [
    'IC', 'LED', 'battery', 'buzzer', 'capacitor', 'clock',
    'connector', 'diode', 'display', 'fuse', 'inductor',
    'potentiometer', 'relay', 'resistor', 'switch', 'transistor'
]

# Page configuration
st.set_page_config(
    page_title="nuts_vision - IC Detector",
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
if DB_AVAILABLE and not st.session_state.get("db_connected", False):
    try:
        st.session_state.db = get_db_manager_from_env()
        st.session_state.db_connected = st.session_state.db.test_connection()
        if st.session_state.db_connected and "db_error" in st.session_state:
            del st.session_state.db_error
    except Exception as e:
        st.session_state.db_connected = False
        st.session_state.db_error = str(e)

# Sidebar
st.sidebar.markdown("## \U0001f527 nuts_vision")
st.sidebar.markdown("**Electronic Component Analyzer**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["\U0001f3e0 Home", "\U0001f4e4 Upload & Process", "\U0001f4f7 PCBA Photo Booth",
     "\U0001f50d Job Viewer", "\U0001f5c4\ufe0f Database Viewer",
     "\U0001f4ca Statistics", "\u2139\ufe0f About"]
)

st.sidebar.markdown("---")
if DB_AVAILABLE:
    if st.session_state.get("db_connected", False):
        st.sidebar.success("\u2705 Database Connected")
    else:
        st.sidebar.warning("\u26a0\ufe0f Database Disconnected")
        if "db_error" in st.session_state:
            st.sidebar.text(f"Error: {st.session_state.db_error}")
        if st.sidebar.button("\U0001f504 Retry Connection"):
            st.session_state.db_connected = False
            if "db_error" in st.session_state:
                del st.session_state.db_error
            st.rerun()
else:
    st.sidebar.warning("\u26a0\ufe0f Database Module Not Available")


# ========== HOME PAGE ==========
if page == "\U0001f3e0 Home":
    st.markdown('<div class="main-header">\U0001f527 nuts_vision</div>', unsafe_allow_html=True)
    st.markdown("### IC Detection System")
    st.markdown("""
    Welcome to **nuts_vision** — an automated system for detecting integrated circuits (ICs) on electronic circuit boards.

    #### \U0001f3af How it works:
    1. **Upload** a photo of an electronic circuit board
    2. **Detect** — YOLOv8 identifies every IC on the board
    3. **Crop** — each detected IC is saved as a separate image
    4. **Browse** — all results are organized in a per-job folder

    #### \U0001f4cb Detected component:
    """)
    st.markdown("\u2713 IC (Integrated Circuit)")

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

    default_model_path = "best.pt"
    model_exists = Path(default_model_path).exists()

    if not model_exists:
        st.warning("""
        \u26a0\ufe0f **Model not found!**
        Make sure `best.pt` is present in the project root directory.
        """)

    st.markdown("### Model Configuration")
    col1, col2 = st.columns([3, 1])
    with col1:
        model_path = st.text_input("Model Path", value=default_model_path if model_exists else "",
                                    help="Path to the trained YOLO model (best.pt)")
    with col2:
        conf_threshold = st.slider("Confidence Threshold", min_value=0.1, max_value=0.9,
                                    value=0.25, step=0.05)

    st.markdown("### Class Filter")
    selected_classes = st.multiselect(
        "Classes to detect (leave empty = detect all)",
        options=COMP_DETECT_CLASSES,
        default=[],
        help="Select which component types to include in the results. Empty means all 16 classes."
    )

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
                        # Apply optional class filter on the metadata
                        dets = result["metadata"]["total_detections"]
                        if selected_classes:
                            filtered = [d for d in result["metadata"]["detections"]
                                        if d["class_name"] in selected_classes]
                            dets = len(filtered)
                        results_summary.append({
                            "file": uploaded_file.name,
                            "status": "\u2705 Success",
                            "job_folder": result["job_folder"],
                            "detections": dets
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



# ========== PCBA PHOTO BOOTH PAGE ==========
elif page == "\U0001f4f7 PCBA Photo Booth":
    st.markdown('<div class="main-header">\U0001f4f7 PCBA Photo Booth</div>', unsafe_allow_html=True)
    st.markdown(
        "Dual-model PCBA inspection pipeline: upload → infer → validate → crop."
    )

    if not DUAL_DETECTOR_AVAILABLE:
        st.error("DualModelDetector could not be imported. Check that `src/detect.py` is present.")
        st.stop()

    # ------------------------------------------------------------------
    # Helper: draw bounding boxes on a PIL image
    # ------------------------------------------------------------------
    def _draw_boxes(pil_img: Image.Image, detections: list) -> Image.Image:
        img = pil_img.copy().convert("RGB")
        draw = ImageDraw.Draw(img)
        palette = {
            'IC': '#FF5733', 'LED': '#33FF57', 'battery': '#3357FF',
            'buzzer': '#FF33A8', 'capacitor': '#33FFF5', 'clock': '#FFD700',
            'connector': '#A833FF', 'diode': '#FF8C00', 'display': '#00CED1',
            'fuse': '#8B4513', 'inductor': '#32CD32', 'potentiometer': '#FF1493',
            'relay': '#1E90FF', 'resistor': '#FF6347', 'switch': '#7CFC00',
            'transistor': '#DC143C',
        }
        for det in detections:
            bbox = det.get('bbox', [])
            if len(bbox) < 4:
                continue
            x1, y1, x2, y2 = [int(v) for v in bbox[:4]]
            cls = det.get('class_name', '?')
            color = palette.get(cls, '#FFFFFF')
            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            label = cls
            if det.get('ic_subtype'):
                label += f" [{det['ic_subtype']}]"
            conf = det.get('confidence', 0)
            label += f" {conf:.2f}"
            draw.text((x1 + 2, max(0, y1 - 14)), label, fill=color)
        return img

    # ------------------------------------------------------------------
    # STEP 1 — Upload
    # ------------------------------------------------------------------
    st.markdown("## Step 1 — Upload Image")
    uploaded = st.file_uploader(
        "Drop a PCB image here",
        type=["jpg", "jpeg", "png"],
        key="pb_upload"
    )

    if uploaded:
        st.session_state["pb_image_bytes"] = uploaded.read()
        # Sanitize: keep only the basename, strip any path separators
        st.session_state["pb_image_name"] = Path(uploaded.name).name
        st.session_state.pop("pb_detections", None)  # reset previous run

    if "pb_image_bytes" not in st.session_state:
        st.info("Upload a PCB image to start.")
        st.stop()

    img_bytes = st.session_state["pb_image_bytes"]
    img_name  = st.session_state["pb_image_name"]
    pil_image = Image.open(io.BytesIO(img_bytes))

    st.image(pil_image, caption=img_name, use_container_width=True)

    # ------------------------------------------------------------------
    # STEP 2 — Model configuration & inference
    # ------------------------------------------------------------------
    st.markdown("## Step 2 — Detection Configuration")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        comp_model_path = st.text_input(
            "comp_detect model path",
            value="comp_detect_best_v2.onnx",
            help="Path to comp_detect_best_v2 (.onnx or .pt)"
        )
        comp_conf = st.slider("comp_detect confidence", 0.1, 0.9, 0.25, 0.05, key="pb_comp_conf")
    with col_m2:
        ic_model_path = st.text_input(
            "ic_detect model path (optional)",
            value="ic_detect_best.onnx",
            help="Path to ic_detect_best (.onnx or .pt) — leave blank to skip IC sub-classification"
        )
        ic_conf = st.slider("ic_detect confidence", 0.1, 0.9, 0.25, 0.05, key="pb_ic_conf")

    st.markdown("### Classes to detect")
    selected_classes = st.multiselect(
        "Select component types (empty = all 16)",
        options=COMP_DETECT_CLASSES,
        default=COMP_DETECT_CLASSES,
        key="pb_class_filter"
    )

    run_inference = st.button("\U0001f50d Run Detection", type="primary")

    if run_inference:
        # Resolve model paths to absolute paths anchored in the project root,
        # accepting only filenames (no directory traversal).
        _project_root = Path(__file__).parent.resolve()
        comp_model_resolved = (_project_root / Path(comp_model_path).name).resolve()
        ic_model_resolved   = (_project_root / Path(ic_model_path).name).resolve() if ic_model_path else None

        # Guard: paths must stay inside the project root
        def _safe_path(p, root):
            try:
                p.relative_to(root)
                return p
            except ValueError:
                return None

        comp_model_resolved = _safe_path(comp_model_resolved, _project_root)
        if ic_model_resolved:
            ic_model_resolved = _safe_path(ic_model_resolved, _project_root)

        if comp_model_resolved is None or not comp_model_resolved.exists():
            st.error(f"comp_detect model not found or path not allowed: {comp_model_path}")
        else:
            # Save image to a temp file for the detector
            tmp_dir = Path("/tmp/pb_uploads")
            tmp_dir.mkdir(parents=True, exist_ok=True)
            tmp_path = (tmp_dir / img_name).resolve()
            tmp_path.write_bytes(img_bytes)

            ic_path_arg = str(ic_model_resolved) if ic_model_resolved and ic_model_resolved.exists() else None
            if ic_model_path and (ic_model_resolved is None or not ic_model_resolved.exists()):
                st.warning(f"ic_detect model not found at '{ic_model_path}' — running single-model mode.")

            with st.spinner("Running dual-model inference…"):
                try:
                    detector = DualModelDetector(
                        comp_model_path=str(comp_model_resolved),
                        ic_model_path=ic_path_arg,
                        comp_conf=comp_conf,
                        ic_conf=ic_conf,
                    )
                    detections = detector.detect(
                        str(tmp_path),
                        class_filter=selected_classes if selected_classes else None
                    )
                    st.session_state["pb_detections"] = detections
                    st.session_state["pb_detection_config"] = {
                        "comp_model": Path(comp_model_path).name,
                        "ic_model": Path(ic_model_path).name if ic_model_path else None,
                        "comp_conf": comp_conf,
                        "ic_conf": ic_conf,
                        "class_filter": selected_classes,
                        "iou_threshold": DualModelDetector.IOU_THRESHOLD,
                    }
                    st.success(f"\u2705 Detected {len(detections)} components.")
                except Exception as exc:
                    import traceback
                    st.error(f"Inference error: {exc}")
                    st.code(traceback.format_exc())

    # ------------------------------------------------------------------
    # STEP 3 — Show annotated image
    # ------------------------------------------------------------------
    if "pb_detections" in st.session_state:
        detections: list = st.session_state["pb_detections"]

        st.markdown("## Step 3 — Annotated Preview")
        annotated = _draw_boxes(pil_image, detections)
        st.image(annotated, caption="Detected components", use_container_width=True)

        # ------------------------------------------------------------------
        # STEP 4 — User validation (editable detection list)
        # ------------------------------------------------------------------
        st.markdown("## Step 4 — Validate & Edit Detections")
        st.markdown(
            "Review the detections below. Uncheck rows to exclude them, "
            "or edit the component type directly."
        )

        # Build an editable dataframe
        rows = []
        for i, d in enumerate(detections):
            rows.append({
                "keep":             True,
                "#":                i,
                "type":             d.get("class_name", ""),
                "ic_subtype":       d.get("ic_subtype") or "",
                "confidence":       round(d.get("confidence", 0), 4),
                "ic_confirmed":     d.get("ic_confirmed", False),
                "x1": round(d["bbox"][0], 1), "y1": round(d["bbox"][1], 1),
                "x2": round(d["bbox"][2], 1), "y2": round(d["bbox"][3], 1),
            })

        df_edit = pd.DataFrame(rows)
        edited_df = st.data_editor(
            df_edit,
            column_config={
                "keep": st.column_config.CheckboxColumn("Keep", default=True),
                "type": st.column_config.SelectboxColumn(
                    "Type", options=COMP_DETECT_CLASSES, required=True
                ),
                "ic_subtype": st.column_config.SelectboxColumn(
                    "IC sub-type", options=["", "four_side", "two_side", "without_side"]
                ),
            },
            disabled=["#", "confidence", "ic_confirmed", "x1", "y1", "x2", "y2"],
            use_container_width=True,
            num_rows="fixed",
            key="pb_edit_df"
        )

        kept_rows = edited_df[edited_df["keep"]]
        st.caption(f"{len(kept_rows)} / {len(detections)} detections kept.")

        # ------------------------------------------------------------------
        # Confirm & generate crops
        # ------------------------------------------------------------------
        if st.button("\u2702\ufe0f Confirm & Generate Crops", type="primary",
                     disabled=len(kept_rows) == 0):
            import cv2
            cv_img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

            crops_dir = Path("/tmp/pb_uploads/crops")
            crops_dir.mkdir(parents=True, exist_ok=True)

            saved_rows = []
            col_imgs = st.columns(4)
            col_idx = 0

            for _, row in kept_rows.iterrows():
                i = int(row["#"])
                d = detections[i]
                bbox = d["bbox"]
                x1, y1, x2, y2 = (max(0, int(v)) for v in bbox[:4])
                # Apply small padding
                pad = 10
                h_img, w_img = cv_img.shape[:2]
                x1c = max(0, x1 - pad)
                y1c = max(0, y1 - pad)
                x2c = min(w_img, x2 + pad)
                y2c = min(h_img, y2 + pad)
                crop = cv_img[y1c:y2c, x1c:x2c]
                cls = row["type"]
                crop_name = f"{i:03d}_{cls}.jpg"
                crop_path = crops_dir / crop_name
                cv2.imwrite(str(crop_path), crop)

                saved_rows.append({
                    "row_number":           i,
                    "detection_type":       cls,
                    "ic_subtype":           row["ic_subtype"] or None,
                    "detection_confidence": float(row["confidence"]),
                    "ic_confidence":        d.get("ic_confidence"),
                    "bounding_box": {
                        "x": x1, "y": y1,
                        "width": x2 - x1, "height": y2 - y1
                    },
                    "cropped_image_path":   str(crop_path),
                    "processing_status":    "pending",
                })

                # Display crop thumbnail
                with col_imgs[col_idx % 4]:
                    st.image(
                        Image.open(io.BytesIO(cv2.imencode(".jpg", crop)[1].tobytes())),
                        caption=f"{cls} ({row['ic_subtype'] or '—'})",
                        use_container_width=True
                    )
                col_idx += 1

            st.success(f"\u2705 {len(saved_rows)} crops generated.")

            # Log to database if available
            config = st.session_state.get("pb_detection_config", {})
            if st.session_state.get("db_connected", False):
                try:
                    with st.session_state.db.get_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute(
                                """
                                INSERT INTO log_pcba_pb_import
                                    (image_storage_path, detection_config, total_detections, status)
                                VALUES (%s, %s, %s, 'completed')
                                RETURNING id
                                """,
                                (
                                    img_name,
                                    json.dumps(config),
                                    len(saved_rows),
                                )
                            )
                            import_id = cur.fetchone()[0]

                        for row_data in saved_rows:
                            with conn.cursor() as cur:
                                cur.execute(
                                    """
                                    INSERT INTO log_pcba_pb_row_import
                                        (log_pcba_pb_import_id, row_number, detection_type,
                                         ic_subtype, detection_confidence, ic_confidence,
                                         bounding_box, cropped_image_path, processing_status)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """,
                                    (
                                        str(import_id),
                                        row_data["row_number"],
                                        row_data["detection_type"],
                                        row_data["ic_subtype"],
                                        row_data["detection_confidence"],
                                        row_data["ic_confidence"],
                                        json.dumps(row_data["bounding_box"]),
                                        row_data["cropped_image_path"],
                                        row_data["processing_status"],
                                    )
                                )
                    st.info(f"\U0001f4be Session logged to database (import id: {import_id})")
                except Exception as exc:
                    st.warning(f"Database logging failed: {exc}")
            else:
                st.info("Database not connected — results not persisted.")


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

    **nuts_vision** analyses photos of electronic circuit boards, detects integrated circuits (ICs),
    and produces cropped images of each detected IC.

    #### \U0001f3af Key Technologies:
    - **YOLOv8**: IC detection (trained model: `best.pt`)
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

    **Version**: 2.1.0 | **License**: CC BY 4.0
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
        default_model = Path("best.pt")
        st.text("Model: \u2705 Found" if default_model.exists() else "Model: \u274c Not found (best.pt missing)")
