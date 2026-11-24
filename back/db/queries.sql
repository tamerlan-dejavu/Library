-- ======================================================================
-- Demonstration queries for the Book Catalog database (read-only)
-- Run: python db/run_sql.py db/queries.sql --out ../docs/sql_results/queries.txt
-- Sections: J = joins, A = aggregates, S = subqueries
-- ======================================================================


-- ----------------------------------------------------------------------
-- JOINS
-- J1 and J2 together use all 11 tables. One query with all 11 tables
-- would multiply rows: a member with 3 loans, 2 phones and 4 reviews
-- would appear 3 * 2 * 4 = 24 times. So J1 follows the "loan" path and
-- J2 brings the other member data (phones, reviews, reservations).
-- ----------------------------------------------------------------------

-- J1. Last 15 loans with full details (INNER JOIN over 8 tables):
--     who borrowed which book, its author, genre and publisher, and which
--     librarian gave it out. Only rows that match in every table remain.
--     A book with two authors gives two rows (one per author).
SELECT l.loan_id,
       l.loan_date,
       m.full_name   AS member,
       b.title,
       a.full_name   AS author,
       c.name        AS genre,
       p.name        AS publisher,
       lib.full_name AS librarian
FROM loan l
INNER JOIN member m       ON m.member_id = l.member_id
INNER JOIN book b         ON b.book_id = l.book_id
INNER JOIN book_author ba ON ba.book_id = b.book_id
INNER JOIN author a       ON a.author_id = ba.author_id
INNER JOIN category c     ON c.category_id = b.category_id
INNER JOIN publisher p    ON p.publisher_id = b.publisher_id
INNER JOIN librarian lib  ON lib.librarian_id = l.librarian_id
ORDER BY l.loan_date DESC, l.loan_id
LIMIT 15;

-- J2. Members with their phones, reviews and reservations (LEFT JOIN).
--     LEFT JOIN keeps a member even when a joined table has no rows for
--     that member (then its columns are NULL and COUNT gives 0).
--     COUNT(DISTINCT ...) removes the duplicates caused by joining
--     three 1:N tables at once.
SELECT m.member_id,
       m.full_name,
       string_agg(DISTINCT mp.phone, ', ')   AS phones,
       COUNT(DISTINCT r.review_id)           AS reviews,
       COUNT(DISTINCT res.reservation_id)    AS reservations
FROM member m
LEFT JOIN member_phone mp ON mp.member_id = m.member_id
LEFT JOIN review r        ON r.member_id = m.member_id
LEFT JOIN reservation res ON res.member_id = m.member_id
GROUP BY m.member_id, m.full_name
ORDER BY reviews DESC, reservations DESC, m.member_id
LIMIT 15;

-- J3. Members who never borrowed a book (RIGHT JOIN).
--     RIGHT JOIN keeps every member (the right table); members without
--     a matching loan get NULL in l.loan_id, and we keep only those.
SELECT m.member_id, m.full_name, m.city
FROM loan l
RIGHT JOIN member m ON m.member_id = l.member_id
WHERE l.loan_id IS NULL
ORDER BY m.member_id;


-- ----------------------------------------------------------------------
-- AGGREGATES (COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING)
-- ----------------------------------------------------------------------

-- A1. Loans per genre: how many, how many are overdue now, and the
--     average loan length in days (for open loans we count until today).
SELECT c.name AS genre,
       COUNT(*) AS loans,
       SUM(CASE WHEN l.return_date IS NULL AND l.due_date < current_date
                THEN 1 ELSE 0 END) AS overdue_now,
       ROUND(AVG(COALESCE(l.return_date, current_date) - l.loan_date), 1) AS avg_days
FROM loan l
JOIN book b     ON b.book_id = l.book_id
JOIN category c ON c.category_id = b.category_id
GROUP BY c.name
ORDER BY loans DESC;

-- A2. Most active members: at least 3 loans (HAVING filters groups,
--     WHERE would filter single rows). Reviews counted by a subquery
--     so that the two counts do not multiply each other.
SELECT m.full_name,
       COUNT(l.loan_id) AS loans,
       (SELECT COUNT(*) FROM review r WHERE r.member_id = m.member_id) AS reviews,
       MIN(l.loan_date) AS first_loan,
       MAX(l.loan_date) AS last_loan
FROM member m
JOIN loan l ON l.member_id = m.member_id
GROUP BY m.member_id, m.full_name
HAVING COUNT(l.loan_id) >= 3
ORDER BY loans DESC, reviews DESC;

-- A3. Books per publisher with the oldest and newest publication year
--     and the total number of copies on the shelves.
SELECT p.name AS publisher,
       COUNT(b.book_id)        AS books,
       MIN(b.publication_year) AS oldest,
       MAX(b.publication_year) AS newest,
       SUM(b.total_copies)     AS copies
FROM publisher p
JOIN book b ON b.publisher_id = p.publisher_id
GROUP BY p.name
ORDER BY books DESC, p.name;


-- ----------------------------------------------------------------------
-- SUBQUERIES
-- ----------------------------------------------------------------------

-- S1. Scalar subquery: books whose average rating is above the average
--     of all reviews. The subquery returns exactly one number.
SELECT b.title,
       ROUND(AVG(r.rating), 2) AS avg_rating,
       COUNT(*) AS reviews
FROM book b
JOIN review r ON r.book_id = b.book_id
GROUP BY b.book_id, b.title
HAVING AVG(r.rating) > (SELECT AVG(rating) FROM review)
ORDER BY avg_rating DESC, reviews DESC
LIMIT 15;

-- S2. EXISTS with a correlated subquery: members who have an overdue loan.
--     The inner query uses m.member_id, so it runs for every member.
SELECT m.member_id, m.full_name, m.email
FROM member m
WHERE EXISTS (SELECT 1
              FROM loan l
              WHERE l.member_id = m.member_id
                AND l.return_date IS NULL
                AND l.due_date < current_date)
ORDER BY m.full_name;

-- S3. NOT EXISTS: books that were never borrowed.
--     (NOT IN would also work here because loan.book_id has no NULLs.)
SELECT b.book_id, b.title
FROM book b
WHERE NOT EXISTS (SELECT 1 FROM loan l WHERE l.book_id = b.book_id)
ORDER BY b.title;

-- S4. IN: authors who wrote at least one bestseller.
--     The subquery returns a list of author ids.
SELECT a.full_name, a.country
FROM author a
WHERE a.author_id IN (SELECT ba.author_id
                      FROM book_author ba
                      JOIN book b ON b.book_id = ba.book_id
                      WHERE b.is_bestseller)
ORDER BY a.full_name;
