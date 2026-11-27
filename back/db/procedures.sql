-- Run order: 3 of 5 (schema -> seed -> procedures -> security -> post_seed_covers); queries.sql, structure.sql and call_functions.sql can run any time after step 4
-- ======================================================================
-- Stored functions (PL/pgSQL). Run after seed.sql. Safe to re-run:
-- CREATE OR REPLACE replaces an existing function with the same name.
-- Each function reuses the logic of one subquery from queries.sql.
-- Column names inside the functions always have a table alias (b., r., ...)
-- so they never clash with the names of the returned columns.
-- ======================================================================


-- ----------------------------------------------------------------------
-- fn_books_above_average_rating
-- Purpose:    books rated better than the average of ALL reviews
--             (same idea as query S1: a scalar subquery).
-- Parameters: min_reviews - ignore books with fewer reviews (default 3)
-- Returns:    book_id, title, avg_rating (2 decimals), review_count
-- Example:    SELECT * FROM fn_books_above_average_rating(2);
-- ----------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_books_above_average_rating(min_reviews INT DEFAULT 3)
RETURNS TABLE (book_id INT, title TEXT, avg_rating NUMERIC, review_count BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT b.book_id, b.title, ROUND(AVG(r.rating), 2), COUNT(*)
    FROM book b
    JOIN review r ON r.book_id = b.book_id
    GROUP BY b.book_id, b.title
    HAVING COUNT(*) >= min_reviews
       -- scalar subquery: one number, the average over all reviews
       AND AVG(r.rating) > (SELECT AVG(r2.rating) FROM review r2)
    ORDER BY 3 DESC, 4 DESC;
END;
$$;


-- ----------------------------------------------------------------------
-- fn_members_with_overdue_loans
-- Purpose:    members who have at least one overdue loan on a given day
--             (same idea as query S2: EXISTS with a correlated subquery).
--             A loan is overdue when it is not returned and due_date < as_of.
-- Parameters: as_of - the day to check (default: today)
-- Returns:    member_id, first_name, last_name, email, overdue_loans,
--             max_days_overdue
-- Example:    SELECT * FROM fn_members_with_overdue_loans();
--             SELECT * FROM fn_members_with_overdue_loans(current_date + 7);
-- ----------------------------------------------------------------------
-- The returned columns changed (full_name -> first_name, last_name, email),
-- and CREATE OR REPLACE cannot change them, so drop the old version first
DROP FUNCTION IF EXISTS fn_members_with_overdue_loans(DATE);

CREATE OR REPLACE FUNCTION fn_members_with_overdue_loans(as_of DATE DEFAULT current_date)
RETURNS TABLE (member_id INT, first_name TEXT, last_name TEXT, email TEXT,
               overdue_loans BIGINT, max_days_overdue INT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT m.member_id,
           m.first_name,
           m.last_name,
           m.email,
           -- correlated subqueries: they use m.member_id of the current row
           (SELECT COUNT(*) FROM loan l
             WHERE l.member_id = m.member_id
               AND l.return_date IS NULL AND l.due_date < as_of),
           (SELECT MAX(as_of - l.due_date) FROM loan l
             WHERE l.member_id = m.member_id
               AND l.return_date IS NULL AND l.due_date < as_of)
    FROM member m
    -- EXISTS keeps only members with at least one overdue loan
    WHERE EXISTS (SELECT 1 FROM loan l
                   WHERE l.member_id = m.member_id
                     AND l.return_date IS NULL AND l.due_date < as_of)
    -- most days overdue first, then by last name and first name
    ORDER BY 6 DESC, 3, 2;
END;
$$;


-- ----------------------------------------------------------------------
-- fn_unborrowed_books
-- Purpose:    books that were never borrowed, optionally of one genre
--             (same idea as query S3: NOT EXISTS).
-- Parameters: genre - category name, any letter case; NULL = all genres
-- Returns:    book_id, title, category_name
-- Example:    SELECT * FROM fn_unborrowed_books();
--             SELECT * FROM fn_unborrowed_books('fantasy');
-- ----------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_unborrowed_books(genre TEXT DEFAULT NULL)
RETURNS TABLE (book_id INT, title TEXT, category_name TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT b.book_id, b.title, c.name
    FROM book b
    LEFT JOIN category c ON c.category_id = b.category_id
    WHERE NOT EXISTS (SELECT 1 FROM loan l WHERE l.book_id = b.book_id)
      AND (genre IS NULL OR c.name ILIKE genre)
    ORDER BY c.name, b.title;
END;
$$;
