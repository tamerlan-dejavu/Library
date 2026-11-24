-- ======================================================================
-- Database structure report (read-only). Shows only the 11 project
-- tables, not Django's own tables (auth_*, django_*).
-- Run: python db/run_sql.py db/structure.sql --out ../docs/sql_results/structure.txt
-- ======================================================================

-- (a) Columns: data type, NULL allowed or not, default value.
--     information_schema.columns describes every column of every table.
SELECT table_name,
       column_name,
       data_type,
       is_nullable,
       column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('category', 'publisher', 'author', 'book', 'book_author',
                     'member', 'member_phone', 'librarian', 'loan',
                     'reservation', 'review')
ORDER BY table_name, ordinal_position;

-- (b) Constraints: PRIMARY KEY, FOREIGN KEY, UNIQUE and CHECK.
--     table_constraints lists them; key_column_usage gives their columns,
--     constraint_column_usage gives the table a FOREIGN KEY points to,
--     check_constraints gives the CHECK condition.
--     PostgreSQL also reports NOT NULL as CHECKs named "..._not_null";
--     they are already visible in (a), so we hide them here.
SELECT tc.table_name,
       tc.constraint_type,
       tc.constraint_name,
       string_agg(DISTINCT kcu.column_name, ', ') AS columns,
       max(ccu.table_name) FILTER (WHERE tc.constraint_type = 'FOREIGN KEY') AS references_table,
       max(cc.check_clause) AS check_clause
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kcu
       ON kcu.constraint_name = tc.constraint_name
      AND kcu.table_schema = tc.table_schema
LEFT JOIN information_schema.constraint_column_usage ccu
       ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
LEFT JOIN information_schema.check_constraints cc
       ON cc.constraint_name = tc.constraint_name
      AND cc.constraint_schema = tc.table_schema
WHERE tc.table_schema = 'public'
  AND tc.table_name IN ('category', 'publisher', 'author', 'book', 'book_author',
                        'member', 'member_phone', 'librarian', 'loan',
                        'reservation', 'review')
  AND tc.constraint_name NOT LIKE '%\_not\_null'
GROUP BY tc.table_name, tc.constraint_type, tc.constraint_name
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

-- (c) Number of rows in each project table, in one result.
--     UNION ALL glues the 11 one-row results together.
SELECT 'category' AS table_name, count(*) AS row_count FROM category
UNION ALL SELECT 'publisher', count(*) FROM publisher
UNION ALL SELECT 'author', count(*) FROM author
UNION ALL SELECT 'book', count(*) FROM book
UNION ALL SELECT 'book_author', count(*) FROM book_author
UNION ALL SELECT 'member', count(*) FROM member
UNION ALL SELECT 'member_phone', count(*) FROM member_phone
UNION ALL SELECT 'librarian', count(*) FROM librarian
UNION ALL SELECT 'loan', count(*) FROM loan
UNION ALL SELECT 'reservation', count(*) FROM reservation
UNION ALL SELECT 'review', count(*) FROM review;
