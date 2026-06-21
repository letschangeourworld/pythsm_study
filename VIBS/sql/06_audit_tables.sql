CREATE TABLE IF NOT EXISTS audit.audit_logs (
    id           BIGSERIAL,
    username     VARCHAR(100),
    user_id      UUID,
    action       VARCHAR(100),
    target_type  VARCHAR(100),
    target_id    UUID,
    ip_address   INET,
    user_agent   TEXT,
    result       VARCHAR(20),
    detail       JSONB,
    created_at   TIMESTAMPTZ  DEFAULT NOW()
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS audit.audit_logs_2026_06 PARTITION OF audit.audit_logs
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
CREATE TABLE IF NOT EXISTS audit.audit_logs_2026_07 PARTITION OF audit.audit_logs
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE IF NOT EXISTS audit.audit_logs_2026_08 PARTITION OF audit.audit_logs
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
CREATE TABLE IF NOT EXISTS audit.audit_logs_2026_09 PARTITION OF audit.audit_logs
    FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');
CREATE TABLE IF NOT EXISTS audit.audit_logs_2026_10 PARTITION OF audit.audit_logs
    FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
CREATE TABLE IF NOT EXISTS audit.audit_logs_2026_11 PARTITION OF audit.audit_logs
    FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');
CREATE TABLE IF NOT EXISTS audit.audit_logs_2026_12 PARTITION OF audit.audit_logs
    FOR VALUES FROM ('2026-12-01') TO ('2027-01-01');

CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit.audit_logs(username, action, target_type, detail)
    VALUES(
        CURRENT_USER, TG_OP,
        TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD)::jsonb
             ELSE row_to_json(NEW)::jsonb END
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
