-- Migration 001 — PCBA Photo Booth logging tables
-- Compatible with standard PostgreSQL and Supabase.
--
-- Supabase-specific features that must be activated manually in Supabase Studio
-- (they are noted as comments and are NOT applied here):
--   • RLS policies  using  is_admin_org()
--   • Realtime publication
--   • FKs to auth.users, organizations, pcba_by_org_ref, log_import_mpn
--     (those tables must already exist in your Supabase project)
--
-- For a plain PostgreSQL setup the tables are self-contained; adjust or
-- remove the FK constraints that reference Supabase-managed tables.

-- ---------------------------------------------------------------------------
-- Enable pgcrypto for gen_random_uuid() if not already available
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------------
-- Table: log_pcba_pb_import
-- One row per Photo Booth PCBA import session
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS log_pcba_pb_import (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at          TIMESTAMPTZ NOT NULL    DEFAULT now(),

    -- Supabase auth / org references — uncomment when those tables exist:
    -- user_id          UUID        REFERENCES auth.users(id),
    -- pcba_id          UUID        REFERENCES pcba_by_org_ref(id),
    -- org_id           UUID        REFERENCES organizations(id),
    user_id             UUID,
    pcba_id             UUID,
    org_id              UUID,

    image_storage_path  TEXT,                           -- path in photo-ocr bucket
    detection_config    JSONB,                          -- confidence thresholds, models, NMS params
    total_detections    INTEGER,                        -- validated detection count
    status              TEXT        NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending','processing','completed','error','cancelled'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_lppi_user_id    ON log_pcba_pb_import (user_id);
CREATE INDEX IF NOT EXISTS idx_lppi_pcba_id    ON log_pcba_pb_import (pcba_id);
CREATE INDEX IF NOT EXISTS idx_lppi_status     ON log_pcba_pb_import (status);
CREATE INDEX IF NOT EXISTS idx_lppi_created_at ON log_pcba_pb_import (created_at DESC);
-- Composite index for concurrency guard (active sessions per user)
CREATE INDEX IF NOT EXISTS idx_lppi_user_active
    ON log_pcba_pb_import (user_id, status)
    WHERE status IN ('pending', 'processing');

-- Supabase: enable RLS
-- ALTER TABLE log_pcba_pb_import ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "admin_org_only" ON log_pcba_pb_import
--     USING (is_admin_org(org_id));

-- Supabase: enable Realtime
-- ALTER PUBLICATION supabase_realtime ADD TABLE log_pcba_pb_import;

-- ---------------------------------------------------------------------------
-- Table: log_pcba_pb_row_import
-- One row per detected object within an import session
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS log_pcba_pb_row_import (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    log_pcba_pb_import_id   UUID        NOT NULL
                                REFERENCES log_pcba_pb_import(id) ON DELETE CASCADE,
    row_number              INTEGER,

    -- Detection fields
    detection_type          TEXT,                       -- one of the 16 comp_detect classes
    ic_subtype              TEXT,                       -- four_side | two_side | without_side (IC only)
    detection_confidence    NUMERIC,                    -- comp_detect confidence score
    ic_confidence           NUMERIC,                   -- ic_detect confidence score (IC only)
    bounding_box            JSONB,                      -- {x, y, width, height} in pixels
    cropped_image_path      TEXT,                       -- path of the crop in photo-ocr bucket

    -- OCR / AI fields (populated in later pipeline stages)
    ocr_text                TEXT,
    description             TEXT,
    interpretation          JSONB,                      -- AI agent result
    ai_candidates           JSONB,                      -- IC candidates
    conversation_id         TEXT,                       -- Mistral conversation ID
    agent_in                JSONB,                      -- agent input for audit
    agent_out               JSONB,                      -- agent output for audit

    -- Links
    -- link_log_import_mpn  UUID REFERENCES log_import_mpn(id),
    link_log_import_mpn     UUID,

    -- Processing status
    processing_status       TEXT        NOT NULL DEFAULT 'pending'
                                CHECK (processing_status IN ('pending','processed','error','cancelled')),
    error_message           TEXT,

    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_lppri_import_id         ON log_pcba_pb_row_import (log_pcba_pb_import_id);
CREATE INDEX IF NOT EXISTS idx_lppri_processing_status ON log_pcba_pb_row_import (processing_status);
CREATE INDEX IF NOT EXISTS idx_lppri_detection_type    ON log_pcba_pb_row_import (detection_type);

-- Supabase: enable RLS
-- ALTER TABLE log_pcba_pb_row_import ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "admin_org_only" ON log_pcba_pb_row_import
--     USING (
--         EXISTS (
--             SELECT 1 FROM log_pcba_pb_import s
--             WHERE s.id = log_pcba_pb_import_id
--               AND is_admin_org(s.org_id)
--         )
--     );

-- Supabase: enable Realtime
-- ALTER PUBLICATION supabase_realtime ADD TABLE log_pcba_pb_row_import;
