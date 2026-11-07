#!/usr/bin/env bash
set -Eeuo pipefail
password="$(cat /run/secrets/team_db_password)"
[[ "$password" =~ ^[0-9a-fA-F]{64}$ ]] || exit 1
psql --username postgres --dbname athena_team -v ON_ERROR_STOP=1 --set=app_password="$password" <<'SQL'
CREATE ROLE athena_team LOGIN PASSWORD :'app_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
ALTER DATABASE athena_team OWNER TO athena_team;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO athena_team;
SQL
