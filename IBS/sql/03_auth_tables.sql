CREATE TABLE IF NOT EXISTS auth.users (
    id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    username     VARCHAR(100) UNIQUE NOT NULL,
    email        VARCHAR(255),
    full_name    VARCHAR(200),
    keycloak_id  VARCHAR(255) UNIQUE,
    enabled      BOOLEAN      DEFAULT TRUE,
    deleted_at   TIMESTAMPTZ,
    created_at   TIMESTAMPTZ  DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username
    ON auth.users(username) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS auth.roles (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name   VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO auth.roles(role_name, description) VALUES
    ('SUPER_ADMIN', '전체 시스템 관리자'),
    ('OPERATOR',    '방송 운영자'),
    ('INTERPRETER', '통역자'),
    ('VIEWER',      '청취자')
ON CONFLICT (role_name) DO NOTHING;

CREATE TABLE IF NOT EXISTS auth.user_roles (
    user_id    UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role_id    UUID REFERENCES auth.roles(id) ON DELETE CASCADE,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);

INSERT INTO auth.users(username, email, full_name, enabled)
VALUES ('admin', 'admin@vitna.net', '시스템 관리자', TRUE)
ON CONFLICT (username) DO NOTHING;

INSERT INTO auth.user_roles(user_id, role_id)
SELECT u.id, r.id FROM auth.users u, auth.roles r
WHERE u.username = 'admin' AND r.role_name = 'SUPER_ADMIN'
ON CONFLICT DO NOTHING;

INSERT INTO auth.users(username, email, full_name, enabled)
VALUES ('interpreter_en', 'interpreter.en@vitna.net', '영어 통역자', TRUE)
ON CONFLICT (username) DO NOTHING;

INSERT INTO auth.user_roles(user_id, role_id)
SELECT u.id, r.id FROM auth.users u, auth.roles r
WHERE u.username = 'interpreter_en' AND r.role_name = 'INTERPRETER'
ON CONFLICT DO NOTHING;
