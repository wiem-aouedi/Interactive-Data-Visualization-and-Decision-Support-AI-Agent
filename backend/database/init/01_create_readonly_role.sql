DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'readonly_user') THEN
        CREATE ROLE readonly_user LOGIN PASSWORD 'REPLACE_WITH_YOUR_ACTUAL_READONLY_DB_PASSWORD';
    END IF;
END
$$;

GRANT SELECT ON products TO readonly_user;
GRANT SELECT ON sales TO readonly_user;
GRANT SELECT ON employees TO readonly_user;
GRANT SELECT ON clients TO readonly_user;