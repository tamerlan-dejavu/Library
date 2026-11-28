-- Run order: 5 of 5 (schema -> seed -> procedures -> security -> post_seed_covers); queries.sql, structure.sql and call_functions.sql can run any time after step 4
-- ======================================================================
-- Five sample books with real covers on the Home page (Bestsellers)
-- and the 12 books of the "Recommended by Tamer" shelf (step 5).
-- Run after seed.sql, procedures.sql and security.sql (this file is the last one):
--     python db/run_sql.py db/post_seed_covers.sql
-- Safe to run again: nothing is inserted twice, the UPDATE gives the
-- same result. Books are found by title, not by a fixed book_id.
-- The cover files are front/covers/<book_id>.jpg; with the data from
-- seed.sql the ids are 1, 3, 4, 73 and 95.
-- ======================================================================

-- The five books in one small table that exists only during this script.
-- alt_title: the same book under another name (UK / US edition).
CREATE TEMP TABLE sample_books (
    title       TEXT,
    alt_title   TEXT,
    author      TEXT,
    birth_year  INT,
    country     TEXT,
    year        INT,
    genre       TEXT,
    description TEXT
) ON COMMIT DROP;

INSERT INTO sample_books VALUES
    ('Harry Potter and the Sorcerer''s Stone', 'Harry Potter and the Philosopher''s Stone',
     'J.K. Rowling', 1965, 'United Kingdom', 1997, 'Fantasy',
     'An orphan learns he is a wizard and starts school at Hogwarts.'),
    ('The Great Gatsby', NULL, 'F. Scott Fitzgerald', 1896, 'United States', 1925, 'Fiction',
     'A mysterious millionaire throws parties to win back a lost love in the Jazz Age.'),
    ('1984', NULL, 'George Orwell', 1903, 'United Kingdom', 1949, 'Fiction',
     'A clerk in a total surveillance state starts to doubt the Party.'),
    ('To Kill a Mockingbird', NULL, 'Harper Lee', 1926, 'United States', 1960, 'Fiction',
     'A child watches her father defend an innocent man in a racist small town.'),
    ('The Da Vinci Code', NULL, 'Dan Brown', 1964, 'United States', 2003, 'Mystery',
     'A murder in the Louvre leads to a chain of hidden codes.');

-- 1. Authors that are missing
INSERT INTO author (full_name, birth_year, country)
SELECT s.author, s.birth_year, s.country
FROM sample_books s
WHERE NOT EXISTS (SELECT 1 FROM author a WHERE a.full_name = s.author);

-- 2. Books that are missing (under either title); any existing publisher
INSERT INTO book (title, publication_year, category_id, publisher_id, description,
                  is_bestseller, total_copies, available_copies)
SELECT s.title, s.year,
       (SELECT c.category_id FROM category c WHERE c.name = s.genre),
       (SELECT min(p.publisher_id) FROM publisher p),
       s.description, true, 3, 3
FROM sample_books s
WHERE NOT EXISTS (SELECT 1 FROM book b
                  WHERE lower(b.title) IN (lower(s.title), lower(coalesce(s.alt_title, s.title))));

-- 3. Book - author links that are missing
INSERT INTO book_author (book_id, author_id)
SELECT b.book_id, a.author_id
FROM sample_books s
JOIN book b   ON lower(b.title) IN (lower(s.title), lower(coalesce(s.alt_title, s.title)))
JOIN author a ON a.full_name = s.author
WHERE NOT EXISTS (SELECT 1 FROM book_author ba
                  WHERE ba.book_id = b.book_id AND ba.author_id = a.author_id);

-- 4. Cover picture and bestseller flag
UPDATE book b
SET cover_url = 'covers/' || b.book_id || '.jpg',
    is_bestseller = true
FROM sample_books s
WHERE lower(b.title) IN (lower(s.title), lower(coalesce(s.alt_title, s.title)));

-- Result: the five books with their ids and covers
SELECT b.book_id, b.title, b.cover_url, b.is_bestseller
FROM book b
JOIN sample_books s ON lower(b.title) IN (lower(s.title), lower(coalesce(s.alt_title, s.title)))
ORDER BY b.book_id;

-- 5. "Recommended by Tamer" shelf on the catalog page: exactly 12 books =
--    the five books above + the 7 other books with the best average rating
--    (at least 2 reviews; the same rating -> the smaller book_id first).
--    One UPDATE for the whole table: true for these 12, false for the rest,
--    so running the script again gives the same 12 books.
UPDATE book
SET is_recommended = book_id IN (
        SELECT b.book_id
        FROM book b
        JOIN sample_books s ON lower(b.title) IN (lower(s.title), lower(coalesce(s.alt_title, s.title)))
    UNION
        SELECT top.book_id
        FROM (SELECT r.book_id
              FROM review r
              JOIN book b ON b.book_id = r.book_id
              WHERE NOT EXISTS (SELECT 1 FROM sample_books s
                                WHERE lower(b.title) IN (lower(s.title), lower(coalesce(s.alt_title, s.title))))
              GROUP BY r.book_id
              HAVING count(*) >= 2
              ORDER BY avg(r.rating) DESC, r.book_id
              LIMIT 7) top
    );

-- Result: the 12 recommended books
SELECT b.book_id, b.title,
       round(avg(r.rating), 2) AS avg_rating, count(r.review_id) AS reviews
FROM book b
LEFT JOIN review r ON r.book_id = b.book_id
WHERE b.is_recommended
GROUP BY b.book_id, b.title
ORDER BY b.book_id;
