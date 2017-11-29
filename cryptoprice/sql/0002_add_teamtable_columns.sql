
ALTER TABLE IF EXISTS team
ADD COLUMN IF NOT EXISTS slack_id varchar(32),
ADD COLUMN IF NOT EXISTS access_token varchar(128),
ADD COLUMN IF NOT EXISTS name varchar(64),
ADD COLUMN IF NOT EXISTS auth jsonb,

ALTER COLUMN slack_id SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS slack_id_index ON team (slack_id);
CREATE INDEX IF NOT EXISTS name_index ON team (name);
