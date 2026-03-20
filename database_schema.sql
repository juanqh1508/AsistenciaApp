-- SQL Schema for Supabase (PostgreSQL)
-- Table: attendance_record

CREATE TABLE IF NOT EXISTS attendance_record (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    ministry_of_service VARCHAR(50) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    shift VARCHAR(50) NOT NULL,
    day_category VARCHAR(20) NOT NULL DEFAULT 'Semana',
    
    -- Main counts
    kids INTEGER DEFAULT 0,
    teens INTEGER DEFAULT 0,
    youth INTEGER DEFAULT 0,
    women INTEGER DEFAULT 0,
    men INTEGER DEFAULT 0,
    
    -- Visits
    visits INTEGER DEFAULT 0,
    visits_kids INTEGER DEFAULT 0,
    visits_teens INTEGER DEFAULT 0,
    visits_youth INTEGER DEFAULT 0,
    visits_men INTEGER DEFAULT 0,
    visits_women INTEGER DEFAULT 0,
    
    -- Testimonies
    testimonies INTEGER DEFAULT 0,
    testimonies_kids INTEGER DEFAULT 0,
    testimonies_teens INTEGER DEFAULT 0,
    testimonies_youth INTEGER DEFAULT 0,
    testimonies_women INTEGER DEFAULT 0,
    testimonies_men INTEGER DEFAULT 0,
    
    -- Converts
    converts_total INTEGER DEFAULT 0,
    converts_kids INTEGER DEFAULT 0,
    converts_teens INTEGER DEFAULT 0,
    converts_youth INTEGER DEFAULT 0,
    converts_men INTEGER DEFAULT 0,
    converts_women INTEGER DEFAULT 0,
    
    -- Reconciled
    reconciled_kids INTEGER DEFAULT 0,
    reconciled_teens INTEGER DEFAULT 0,
    reconciled_youth INTEGER DEFAULT 0,
    reconciled_men INTEGER DEFAULT 0,
    reconciled_women INTEGER DEFAULT 0
);

-- Index for date queries
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance_record(date);
