-- UWB 위치 추적 시스템 스키마
 
-- 태그 마스터
CREATE TABLE IF NOT EXISTS tags (
    id          SERIAL PRIMARY KEY,
    tag_id      VARCHAR(64) UNIQUE NOT NULL,
    label       VARCHAR(128),              -- "작업자A", "지게차-01"
    tag_type    VARCHAR(32) DEFAULT 'worker', -- worker | vehicle | asset
    active      BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
 
-- 위치 로그 (파티션 테이블 - 월별)
CREATE TABLE IF NOT EXISTS location_logs (
    id          BIGSERIAL,
    tag_id      VARCHAR(64)   NOT NULL,
    x           FLOAT         NOT NULL,   -- 실수 좌표 (미터)
    y           FLOAT         NOT NULL,
    z           FLOAT         DEFAULT 0,
    zone_id     VARCHAR(64),              -- 구역 코드
    floor       SMALLINT      DEFAULT 1,
    ts          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    raw_data    JSONB,                    -- 원본 UWB 데이터
    PRIMARY KEY (id, ts)
) PARTITION BY RANGE (ts);
 
-- 월별 파티션 생성 (최근 3개월)
CREATE TABLE location_logs_2025_01 PARTITION OF location_logs
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE location_logs_2025_02 PARTITION OF location_logs
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE location_logs_2025_03 PARTITION OF location_logs
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE location_logs_2025_04 PARTITION OF location_logs
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE location_logs_2025_05 PARTITION OF location_logs
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
CREATE TABLE location_logs_2025_06 PARTITION OF location_logs
    FOR VALUES FROM ('2025-06-01') TO ('2026-01-01');
CREATE TABLE location_logs_default PARTITION OF location_logs DEFAULT;
 
-- 이상 탐지 이벤트
CREATE TABLE IF NOT EXISTS anomaly_events (
    id          BIGSERIAL PRIMARY KEY,
    tag_id      VARCHAR(64)  NOT NULL,
    event_type  VARCHAR(64)  NOT NULL,  -- out_of_zone | speed_violation | isolation_forest | lstm_anomaly
    score       FLOAT,                  -- 이상 점수 (0~1)
    description TEXT,
    location    JSONB,                  -- {x, y, zone_id}
    resolved    BOOLEAN DEFAULT FALSE,
    ts          TIMESTAMPTZ DEFAULT NOW()
);
 
-- 공장 구역 정의
CREATE TABLE IF NOT EXISTS zones (
    id          SERIAL PRIMARY KEY,
    zone_id     VARCHAR(64) UNIQUE NOT NULL,
    name        VARCHAR(128) NOT NULL,
    floor       SMALLINT DEFAULT 1,
    polygon     JSONB NOT NULL,  -- [[x1,y1],[x2,y2],...]
    danger_level SMALLINT DEFAULT 0,  -- 0:일반 1:주의 2:위험
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
 
-- 인덱스
CREATE INDEX idx_location_logs_tag_ts  ON location_logs (tag_id, ts DESC);
CREATE INDEX idx_location_logs_ts      ON location_logs (ts DESC);
CREATE INDEX idx_location_logs_zone    ON location_logs (zone_id, ts DESC);
CREATE INDEX idx_anomaly_tag_ts        ON anomaly_events (tag_id, ts DESC);
CREATE INDEX idx_anomaly_unresolved    ON anomaly_events (resolved, ts DESC) WHERE resolved = FALSE;
 
-- 샘플 데이터
INSERT INTO tags (tag_id, label, tag_type) VALUES
    ('TAG001', '작업자-김철수', 'worker'),
    ('TAG002', '작업자-이영희', 'worker'),
    ('TAG003', '지게차-01', 'vehicle'),
    ('TAG004', '지게차-02', 'vehicle'),
    ('TAG005', '팔레트-A', 'asset');
 
INSERT INTO zones (zone_id, name, floor, polygon, danger_level) VALUES
    ('ZONE_A', '조립구역', 1, '[[0,0],[50,0],[50,30],[0,30]]', 1),
    ('ZONE_B', '용접구역', 1, '[[55,0],[100,0],[100,30],[55,30]]', 2),
    ('ZONE_C', '사무실', 1, '[[0,35],[40,35],[40,60],[0,60]]', 0);