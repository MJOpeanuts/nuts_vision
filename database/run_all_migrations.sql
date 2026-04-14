-- ==========================================================================
-- nuts_vision — Complete Database Migration
-- ==========================================================================
-- This file creates the entire nuts_vision database schema from scratch.
-- It is safe to re-run: every statement uses IF NOT EXISTS.
--
-- Usage:
--   psql -h <host> -U nuts_user -d nuts_vision -f database/run_all_migrations.sql
--
-- Or via Docker:
--   docker exec -i nuts_vision_db psql -U nuts_user -d nuts_vision < database/run_all_migrations.sql
-- ==========================================================================

BEGIN;

-- =========================================================================
-- 0. Migration tracking table
-- =========================================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     INTEGER     PRIMARY KEY,
    name        TEXT        NOT NULL,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================================
-- 1. Initial schema  (init.sql)
-- =========================================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM schema_migrations WHERE version = 0) THEN

        -- Table: images_input
        CREATE TABLE IF NOT EXISTS images_input (
            image_id    SERIAL      PRIMARY KEY,
            file_name   VARCHAR(255) NOT NULL,
            file_path   TEXT         NOT NULL,
            upload_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            format      VARCHAR(10)
        );

        -- Table: log_jobs
        CREATE TABLE IF NOT EXISTS log_jobs (
            job_id          SERIAL      PRIMARY KEY,
            image_id        INTEGER     NOT NULL,
            job_name        VARCHAR(255),
            job_folder_path TEXT,
            started_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
            ended_at        TIMESTAMP,
            model           VARCHAR(255),
            FOREIGN KEY (image_id) REFERENCES images_input(image_id) ON DELETE CASCADE
        );

        -- Table: detections
        CREATE TABLE IF NOT EXISTS detections (
            detection_id    SERIAL      PRIMARY KEY,
            job_id          INTEGER     NOT NULL,
            class_name      VARCHAR(50) NOT NULL,
            confidence      FLOAT       NOT NULL,
            bbox_x1         FLOAT       NOT NULL,
            bbox_y1         FLOAT       NOT NULL,
            bbox_x2         FLOAT       NOT NULL,
            bbox_y2         FLOAT       NOT NULL,
            FOREIGN KEY (job_id) REFERENCES log_jobs(job_id) ON DELETE CASCADE
        );

        -- Table: ics_cropped
        CREATE TABLE IF NOT EXISTS ics_cropped (
            cropped_id          SERIAL      PRIMARY KEY,
            job_id              INTEGER     NOT NULL,
            detection_id        INTEGER     NOT NULL,
            cropped_file_path   TEXT        NOT NULL,
            created_at          TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id)        REFERENCES log_jobs(job_id)       ON DELETE CASCADE,
            FOREIGN KEY (detection_id)  REFERENCES detections(detection_id) ON DELETE CASCADE
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_log_jobs_image_id        ON log_jobs(image_id);
        CREATE INDEX IF NOT EXISTS idx_detections_job_id        ON detections(job_id);
        CREATE INDEX IF NOT EXISTS idx_ics_cropped_job_id       ON ics_cropped(job_id);
        CREATE INDEX IF NOT EXISTS idx_ics_cropped_detection_id ON ics_cropped(detection_id);

        INSERT INTO schema_migrations (version, name) VALUES (0, 'init');
        RAISE NOTICE 'Applied migration 0 — init';
    ELSE
        RAISE NOTICE 'Migration 0 (init) already applied, skipping';
    END IF;
END
$$;

-- =========================================================================
-- 2. PCBA Photo Booth logging (migration_001_pcba_logging.sql)
-- =========================================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM schema_migrations WHERE version = 1) THEN

        -- Enable pgcrypto for gen_random_uuid()
        CREATE EXTENSION IF NOT EXISTS pgcrypto;

        -- Table: log_pcba_pb_import
        CREATE TABLE IF NOT EXISTS log_pcba_pb_import (
            id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            created_at          TIMESTAMPTZ NOT NULL    DEFAULT now(),
            user_id             UUID,
            pcba_id             UUID,
            org_id              UUID,
            image_storage_path  TEXT,
            detection_config    JSONB,
            total_detections    INTEGER,
            status              TEXT        NOT NULL DEFAULT 'pending'
                                    CHECK (status IN ('pending','processing','completed','error','cancelled'))
        );

        CREATE INDEX IF NOT EXISTS idx_lppi_user_id     ON log_pcba_pb_import (user_id);
        CREATE INDEX IF NOT EXISTS idx_lppi_pcba_id     ON log_pcba_pb_import (pcba_id);
        CREATE INDEX IF NOT EXISTS idx_lppi_status      ON log_pcba_pb_import (status);
        CREATE INDEX IF NOT EXISTS idx_lppi_created_at  ON log_pcba_pb_import (created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_lppi_user_active
            ON log_pcba_pb_import (user_id, status)
            WHERE status IN ('pending', 'processing');

        -- Table: log_pcba_pb_row_import
        CREATE TABLE IF NOT EXISTS log_pcba_pb_row_import (
            id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            log_pcba_pb_import_id   UUID        NOT NULL
                                        REFERENCES log_pcba_pb_import(id) ON DELETE CASCADE,
            row_number              INTEGER,
            detection_type          TEXT,
            ic_subtype              TEXT,
            detection_confidence    NUMERIC,
            ic_confidence           NUMERIC,
            bounding_box            JSONB,
            cropped_image_path      TEXT,
            ocr_text                TEXT,
            description             TEXT,
            interpretation          JSONB,
            ai_candidates           JSONB,
            conversation_id         TEXT,
            agent_in                JSONB,
            agent_out               JSONB,
            link_log_import_mpn     UUID,
            processing_status       TEXT        NOT NULL DEFAULT 'pending'
                                        CHECK (processing_status IN ('pending','processed','error','cancelled')),
            error_message           TEXT,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS idx_lppri_import_id          ON log_pcba_pb_row_import (log_pcba_pb_import_id);
        CREATE INDEX IF NOT EXISTS idx_lppri_processing_status  ON log_pcba_pb_row_import (processing_status);
        CREATE INDEX IF NOT EXISTS idx_lppri_detection_type     ON log_pcba_pb_row_import (detection_type);

        INSERT INTO schema_migrations (version, name) VALUES (1, 'pcba_logging');
        RAISE NOTICE 'Applied migration 1 — pcba_logging';
    ELSE
        RAISE NOTICE 'Migration 1 (pcba_logging) already applied, skipping';
    END IF;
END
$$;

COMMIT;

-- =========================================================================
-- Summary
-- =========================================================================
\echo ''
\echo '=== nuts_vision — Migration Summary ==='
SELECT version, name, applied_at FROM schema_migrations ORDER BY version;
\echo '======================================='
\echo 'All migrations applied successfully!'
