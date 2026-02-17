#!/usr/bin/env python3
"""
Database utilities for nuts_vision
Manages PostgreSQL database connections and logging operations.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, Dict, List, Any
import os
from datetime import datetime


class DatabaseManager:
    """Manages database connections and operations for nuts_vision."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "nuts_vision",
        user: str = "nuts_user",
        password: str = "nuts_password"
    ):
        """
        Initialize database manager.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        
    @contextmanager
    def get_connection(self):
        """Get a database connection context manager."""
        conn = psycopg2.connect(**self.connection_params)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def log_image_upload(
        self,
        file_name: str,
        file_path: str,
        format: str = None
    ) -> int:
        """
        Log an uploaded image to the database.
        
        Args:
            file_name: Name of the image file
            file_path: Full path to the image file
            format: Image format (e.g., 'jpg', 'png')
            
        Returns:
            image_id of the inserted record
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO images_input (file_name, file_path, format)
                    VALUES (%s, %s, %s)
                    RETURNING image_id
                    """,
                    (file_name, file_path, format)
                )
                image_id = cursor.fetchone()[0]
                return image_id
    
    def start_job(
        self,
        image_id: int,
        model: str
    ) -> int:
        """
        Start a detection job.
        
        Args:
            image_id: ID of the image being processed
            model: Model name/path used for detection
            
        Returns:
            job_id of the created job
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO log_jobs (image_id, model)
                    VALUES (%s, %s)
                    RETURNING job_id
                    """,
                    (image_id, model)
                )
                job_id = cursor.fetchone()[0]
                return job_id
    
    def end_job(self, job_id: int):
        """
        Mark a job as ended.
        
        Args:
            job_id: ID of the job to end
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE log_jobs
                    SET ended_at = CURRENT_TIMESTAMP
                    WHERE job_id = %s
                    """,
                    (job_id,)
                )
    
    def log_detection(
        self,
        job_id: int,
        class_name: str,
        confidence: float,
        bbox: List[float]
    ) -> int:
        """
        Log a detection result.
        
        Args:
            job_id: ID of the job
            class_name: Detected component class
            confidence: Detection confidence score
            bbox: Bounding box coordinates [x1, y1, x2, y2]
            
        Returns:
            detection_id of the inserted record
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO detections 
                    (job_id, class_name, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING detection_id
                    """,
                    (job_id, class_name, confidence, bbox[0], bbox[1], bbox[2], bbox[3])
                )
                detection_id = cursor.fetchone()[0]
                return detection_id
    
    def log_cropped_ic(
        self,
        job_id: int,
        detection_id: int,
        cropped_file_path: str
    ) -> int:
        """
        Log a cropped IC image.
        
        Args:
            job_id: ID of the job
            detection_id: ID of the detection
            cropped_file_path: Path to the cropped image
            
        Returns:
            cropped_id of the inserted record
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO ics_cropped (job_id, detection_id, cropped_file_path)
                    VALUES (%s, %s, %s)
                    RETURNING cropped_id
                    """,
                    (job_id, detection_id, cropped_file_path)
                )
                cropped_id = cursor.fetchone()[0]
                return cropped_id
    
    def log_ocr_result(
        self,
        job_id: int,
        cropped_id: int,
        raw_text: str,
        cleaned_mpn: str,
        rotation_angle: int,
        confidence: float = None
    ) -> int:
        """
        Log an OCR result.
        
        Args:
            job_id: ID of the job
            cropped_id: ID of the cropped IC
            raw_text: Raw OCR text
            cleaned_mpn: Cleaned MPN
            rotation_angle: Angle at which OCR was performed (0, 90, 180, 270)
            confidence: OCR confidence score
            
        Returns:
            ocr_id of the inserted record
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO ics_ocr 
                    (job_id, cropped_id, raw_text, cleaned_mpn, rotation_angle, confidence)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING ocr_id
                    """,
                    (job_id, cropped_id, raw_text, cleaned_mpn, rotation_angle, confidence)
                )
                ocr_id = cursor.fetchone()[0]
                return ocr_id
    
    def get_job_statistics(self, job_id: int) -> Dict[str, Any]:
        """
        Get statistics for a specific job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Dictionary with job statistics
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get job info
                cursor.execute(
                    """
                    SELECT 
                        j.*,
                        i.file_name,
                        i.file_path,
                        COUNT(DISTINCT d.detection_id) as total_detections,
                        COUNT(DISTINCT ic.cropped_id) as total_ics_cropped,
                        COUNT(DISTINCT o.ocr_id) as total_ocr_results
                    FROM log_jobs j
                    JOIN images_input i ON j.image_id = i.image_id
                    LEFT JOIN detections d ON j.job_id = d.job_id
                    LEFT JOIN ics_cropped ic ON j.job_id = ic.job_id
                    LEFT JOIN ics_ocr o ON j.job_id = o.job_id
                    WHERE j.job_id = %s
                    GROUP BY j.job_id, i.file_name, i.file_path
                    """,
                    (job_id,)
                )
                stats = cursor.fetchone()
                return dict(stats) if stats else {}
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def get_all_images(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all uploaded images.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of image records
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT * FROM images_input
                    ORDER BY upload_at DESC
                    LIMIT %s
                    """,
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
    
    def get_all_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all jobs with image information.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of job records
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT 
                        j.*,
                        i.file_name,
                        i.file_path,
                        i.format,
                        COUNT(DISTINCT d.detection_id) as detection_count
                    FROM log_jobs j
                    JOIN images_input i ON j.image_id = i.image_id
                    LEFT JOIN detections d ON j.job_id = d.job_id
                    GROUP BY j.job_id, i.file_name, i.file_path, i.format
                    ORDER BY j.started_at DESC
                    LIMIT %s
                    """,
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
    
    def get_all_detections(self, job_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all detections, optionally filtered by job.
        
        Args:
            job_id: Optional job ID to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of detection records
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if job_id:
                    cursor.execute(
                        """
                        SELECT * FROM detections
                        WHERE job_id = %s
                        ORDER BY detection_id DESC
                        LIMIT %s
                        """,
                        (job_id, limit)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT * FROM detections
                        ORDER BY detection_id DESC
                        LIMIT %s
                        """,
                        (limit,)
                    )
                return [dict(row) for row in cursor.fetchall()]
    
    def get_all_ocr_results(self, job_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all OCR results, optionally filtered by job.
        
        Args:
            job_id: Optional job ID to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of OCR records with cropped image paths
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if job_id:
                    cursor.execute(
                        """
                        SELECT 
                            o.*,
                            ic.cropped_file_path,
                            d.class_name
                        FROM ics_ocr o
                        JOIN ics_cropped ic ON o.cropped_id = ic.cropped_id
                        JOIN detections d ON ic.detection_id = d.detection_id
                        WHERE o.job_id = %s
                        ORDER BY o.processed_at DESC
                        LIMIT %s
                        """,
                        (job_id, limit)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT 
                            o.*,
                            ic.cropped_file_path,
                            d.class_name
                        FROM ics_ocr o
                        JOIN ics_cropped ic ON o.cropped_id = ic.cropped_id
                        JOIN detections d ON ic.detection_id = d.detection_id
                        ORDER BY o.processed_at DESC
                        LIMIT %s
                        """,
                        (limit,)
                    )
                return [dict(row) for row in cursor.fetchall()]
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """
        Get overall detection statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT 
                        COUNT(DISTINCT i.image_id) as total_images,
                        COUNT(DISTINCT j.job_id) as total_jobs,
                        COUNT(DISTINCT d.detection_id) as total_detections,
                        COUNT(DISTINCT o.ocr_id) as total_ocr_results,
                        COUNT(DISTINCT CASE WHEN o.cleaned_mpn IS NOT NULL AND o.cleaned_mpn != '' THEN o.ocr_id END) as successful_mpn_extractions
                    FROM images_input i
                    LEFT JOIN log_jobs j ON i.image_id = j.image_id
                    LEFT JOIN detections d ON j.job_id = d.job_id
                    LEFT JOIN ics_ocr o ON j.job_id = o.job_id
                    """
                )
                stats = cursor.fetchone()
                
                # Get component counts
                cursor.execute(
                    """
                    SELECT class_name, COUNT(*) as count
                    FROM detections
                    GROUP BY class_name
                    ORDER BY count DESC
                    """
                )
                component_counts = {row['class_name']: row['count'] for row in cursor.fetchall()}
                
                result = dict(stats) if stats else {}
                result['component_counts'] = component_counts
                return result


def get_db_manager_from_env() -> DatabaseManager:
    """
    Create a DatabaseManager using environment variables.
    
    Environment variables:
        DB_HOST: Database host (default: localhost)
        DB_PORT: Database port (default: 5432)
        DB_NAME: Database name (default: nuts_vision)
        DB_USER: Database user (default: nuts_user)
        DB_PASSWORD: Database password (default: nuts_password)
    
    Returns:
        DatabaseManager instance
    """
    return DatabaseManager(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
        database=os.getenv('DB_NAME', 'nuts_vision'),
        user=os.getenv('DB_USER', 'nuts_user'),
        password=os.getenv('DB_PASSWORD', 'nuts_password')
    )
