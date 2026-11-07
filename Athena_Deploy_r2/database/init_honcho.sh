#!/usr/bin/env bash
set -Eeuo pipefail
password="$(cat /run/secrets/honcho_db_password)"
[[ "$password" =~ ^[0-9a-fA-F]{64}$ ]] || exit 1
psql --username postgres --dbname honcho -v ON_ERROR_STOP=1 --set=app_password="$password" <<'SQL'
CREATE ROLE honcho LOGIN PASSWORD :'app_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
ALTER DATABASE honcho OWNER TO honcho;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO honcho;
SQL
