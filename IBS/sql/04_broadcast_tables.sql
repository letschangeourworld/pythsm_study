CREATE TABLE IF NOT EXISTS broadcast.rooms (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    room_name     VARCHAR(100) UNIQUE NOT NULL,
    language_code VARCHAR(10)  NOT NULL,
    language_name VARCHAR(50),
    active        BOOLEAN      DEFAULT TRUE,
    created_at    TIMESTAMPTZ  DEFAULT NOW()
);

INSERT INTO broadcast.rooms(room_name, language_code, language_name) VALUES
    ('room_ko', 'KO', '한국어'),
    ('room_en', 'EN', 'English'),
    ('room_ja', 'JA', '日本語'),
    ('room_zh', 'ZH', '中文')
ON CONFLICT (room_name) DO NOTHING;

CREATE TABLE IF NOT EXISTS broadcast.sessions (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id     UUID         REFERENCES broadcast.rooms(id),
    title       VARCHAR(255),
    description TEXT,
    status      VARCHAR(20)  DEFAULT 'READY',
    start_time  TIMESTAMPTZ,
    end_time    TIMESTAMPTZ,
    created_by  UUID         REFERENCES auth.users(id),
    created_at  TIMESTAMPTZ  DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_status ON broadcast.sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_created ON broadcast.sessions(created_at DESC);

CREATE TABLE IF NOT EXISTS broadcast.listener_sessions (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID         REFERENCES broadcast.sessions(id),
    room_name        VARCHAR(100),
    language_code    VARCHAR(10),
    connected_at     TIMESTAMPTZ  DEFAULT NOW(),
    disconnected_at  TIMESTAMPTZ,
    ip_address       INET,
    user_agent       TEXT
);

CREATE TABLE IF NOT EXISTS broadcast.interpreter_sessions (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    interpreter_id  UUID         REFERENCES auth.users(id),
    session_id      UUID         REFERENCES broadcast.sessions(id),
    room_name       VARCHAR(100),
    login_time      TIMESTAMPTZ  DEFAULT NOW(),
    logout_time     TIMESTAMPTZ,
    last_heartbeat  TIMESTAMPTZ  DEFAULT NOW(),
    status          VARCHAR(20)  DEFAULT 'ONLINE'
);

CREATE TABLE IF NOT EXISTS broadcast.recordings (
    id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id     UUID         REFERENCES broadcast.sessions(id),
    object_path    TEXT         NOT NULL,
    language_code  VARCHAR(10),
    duration_sec   INTEGER,
    file_size      BIGINT,
    status         VARCHAR(20)  DEFAULT 'COMPLETED',
    created_at     TIMESTAMPTZ  DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS broadcast.subtitles (
    id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id     UUID         REFERENCES broadcast.sessions(id),
    language_code  VARCHAR(10),
    object_path    TEXT,
    created_at     TIMESTAMPTZ  DEFAULT NOW()
);
