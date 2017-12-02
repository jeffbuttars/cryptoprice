CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS team (
    id uuid DEFAULT gen_random_uuid(),
    PRIMARY KEY (id)
);
