CREATE TABLE IF NOT EXISTS monitoring.system_events (
    id          BIGSERIAL    PRIMARY KEY,
    event_type  VARCHAR(50),
    severity    VARCHAR(20),
    service     VARCHAR(50),
    message     TEXT,
    detail      JSONB,
    resolved    BOOLEAN      DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ  DEFAULT NOW()
);
