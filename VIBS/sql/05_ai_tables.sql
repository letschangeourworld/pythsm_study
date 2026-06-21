CREATE TABLE IF NOT EXISTS ai.stt_logs (
    id             BIGSERIAL,
    session_id     UUID,
    room_name      VARCHAR(100),
    language_code  VARCHAR(10),
    recognized_text TEXT,
    confidence     NUMERIC(5,4),
    latency_ms     INTEGER,
    model_name     VARCHAR(100) DEFAULT 'faster-whisper-large-v3',
    created_at     TIMESTAMPTZ  DEFAULT NOW()
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS ai.stt_logs_2026_06 PARTITION OF ai.stt_logs
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
CREATE TABLE IF NOT EXISTS ai.stt_logs_2026_07 PARTITION OF ai.stt_logs
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE IF NOT EXISTS ai.stt_logs_2026_08 PARTITION OF ai.stt_logs
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
CREATE TABLE IF NOT EXISTS ai.stt_logs_2026_09 PARTITION OF ai.stt_logs
    FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');
CREATE TABLE IF NOT EXISTS ai.stt_logs_2026_10 PARTITION OF ai.stt_logs
    FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
CREATE TABLE IF NOT EXISTS ai.stt_logs_2026_11 PARTITION OF ai.stt_logs
    FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');
CREATE TABLE IF NOT EXISTS ai.stt_logs_2026_12 PARTITION OF ai.stt_logs
    FOR VALUES FROM ('2026-12-01') TO ('2027-01-01');

CREATE TABLE IF NOT EXISTS ai.translation_logs (
    id               BIGSERIAL    PRIMARY KEY,
    session_id       UUID,
    source_language  VARCHAR(10),
    target_language  VARCHAR(10),
    source_text      TEXT,
    translated_text  TEXT,
    model_name       VARCHAR(100) DEFAULT 'nllb-200-3.3b',
    latency_ms       INTEGER,
    confidence       NUMERIC(5,4),
    from_memory      BOOLEAN      DEFAULT FALSE,
    created_at       TIMESTAMPTZ  DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai.tts_logs (
    id             BIGSERIAL    PRIMARY KEY,
    session_id     UUID,
    language_code  VARCHAR(10),
    voice_name     VARCHAR(100),
    input_text     TEXT,
    audio_path     TEXT,
    latency_ms     INTEGER,
    created_at     TIMESTAMPTZ  DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai.translation_memory (
    id               BIGSERIAL    PRIMARY KEY,
    source_language  VARCHAR(10)  NOT NULL,
    target_language  VARCHAR(10)  NOT NULL,
    source_text      TEXT         NOT NULL,
    translated_text  TEXT         NOT NULL,
    embedding        VECTOR(1024),
    usage_count      INTEGER      DEFAULT 0,
    verified         BOOLEAN      DEFAULT FALSE,
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tm_embedding_hnsw
    ON ai.translation_memory
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_tm_lang_pair
    ON ai.translation_memory(source_language, target_language);

INSERT INTO ai.translation_memory
    (source_language, target_language, source_text, translated_text, verified)
VALUES
    ('ko', 'en', '구원', 'Salvation', TRUE),
    ('ko', 'en', '은혜', 'Grace', TRUE),
    ('ko', 'en', '복음', 'Gospel', TRUE),
    ('ko', 'en', '성화', 'Sanctification', TRUE),
    ('ko', 'en', '성령', 'Holy Spirit', TRUE),
    ('ko', 'en', '회개', 'Repentance', TRUE),
    ('ko', 'en', '구속', 'Redemption', TRUE),
    ('ko', 'en', '믿음', 'Faith', TRUE),
    ('ko', 'en', '기도', 'Prayer', TRUE),
    ('ko', 'en', '예배', 'Worship', TRUE),
    ('ko', 'en', '설교', 'Sermon', TRUE),
    ('ko', 'en', '교회', 'Church', TRUE),
    ('ko', 'en', '하나님', 'God', TRUE),
    ('ko', 'en', '예수님', 'Jesus Christ', TRUE),
    ('ko', 'en', '성경', 'Bible', TRUE)
ON CONFLICT DO NOTHING;
