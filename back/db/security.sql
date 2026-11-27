-- ======================================================================
-- Security: an application role with only the rights the website needs.
-- Run as the admin user (postgres) AFTER migrate, schema, seed, procedures,
-- post_seed_covers (this file is always the last one):
--     python db/run_sql.py db/security.sql
-- The password below is a placeholder (app_password with a colon in
-- front). run_sql.py replaces it with the environment variable
-- APP_DB_PASSWORD, so no real password is ever written into this file.
-- Safe to run again: existing role and policies are updated, not duplicated.
-- ======================================================================


-- 1. The role. LOGIN = it can connect. Everything else is "NO" by default:
--    no superuser, no CREATEDB, no CREATEROLE. If the role already exists,
--    only its password is updated.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'library_app') THEN
        CREATE ROLE library_app LOGIN PASSWORD :app_password
            NOSUPERUSER NOCREATEDB NOCREATEROLE;
    ELSE
        -- Only LOGIN and the password; on Supabase even "NOSUPERUSER"
        -- in ALTER ROLE needs superuser rights
        ALTER ROLE library_app LOGIN PASSWORD :app_password;
    END IF;
END
$$;


-- 2. Connect to this database and see the objects in schema public.
--    USAGE lets the role find tables in the schema, but NOT create new ones
--    (that would be the CREATE privilege, which we do not give).
DO $$
BEGIN
    EXECUTE format('GRANT CONNECT ON DATABASE %I TO library_app', current_database());
END
$$;
GRANT USAGE ON SCHEMA public TO library_app;
REVOKE CREATE ON SCHEMA public FROM library_app;


-- 3. Data rights only: read and change rows in every table of schema
--    public (our 11 tables and Django's auth_* / django_* tables).
--    No TRUNCATE, no ALTER, no DROP: only the owner (postgres) can do that.
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO library_app;

-- Identity columns take their next id from a sequence
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO library_app;

-- Our stored functions (procedures.sql)
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO library_app;

-- The same rights for tables and sequences that postgres creates later
-- (for example after running schema.sql again)
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO library_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO library_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT EXECUTE ON FUNCTIONS TO library_app;


-- 4. Row level security (RLS). Supabase turns RLS on for tables; with RLS
--    on and no policy, a normal role sees zero rows. We keep RLS on and add
--    one policy that lets library_app use all rows. Other roles get no
--    policy, so they still see nothing. The table owner (postgres) is not
--    limited by RLS.
DO $$
DECLARE
    t RECORD;
BEGIN
    FOR t IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t.tablename);
        EXECUTE format('DROP POLICY IF EXISTS app_full_access ON public.%I', t.tablename);
        EXECUTE format('CREATE POLICY app_full_access ON public.%I FOR ALL TO library_app '
                       'USING (true) WITH CHECK (true)', t.tablename);
    END LOOP;
END
$$;


-- 5. Close Supabase's public HTTP API (roles anon and authenticated).
--    The website talks to the database only through Django, so these roles
--    need no rights on our tables, now or in the future.
DO $$
DECLARE
    r TEXT;
BEGIN
    FOREACH r IN ARRAY ARRAY['anon', 'authenticated'] LOOP
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
            EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA public FROM %I', r);
            EXECUTE format('REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM %I', r);
            EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM %I', r);
        END IF;
    END LOOP;
END
$$;


-- 6. Short report: the rights library_app has on each project table
SELECT c.relname AS table_name,
       has_table_privilege('library_app', c.oid, 'SELECT') AS can_select,
       has_table_privilege('library_app', c.oid, 'INSERT') AS can_insert,
       has_table_privilege('library_app', c.oid, 'UPDATE') AS can_update,
       has_table_privilege('library_app', c.oid, 'DELETE') AS can_delete,
       c.relrowsecurity AS rls_on
FROM pg_class c
WHERE c.relnamespace = 'public'::regnamespace
  AND c.relkind = 'r'
ORDER BY c.relname;
