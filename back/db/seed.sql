-- Demo data. Run right after schema.sql (tables are empty, so IDs start at 1
-- and follow the insert order; the numbers in comments are those IDs).

-- 1 Fiction, 2 Non-Fiction, 3 Fantasy, 4 Sci-Fi, 5 Mystery, 6 Biography
INSERT INTO category (name) VALUES
    ('Fiction'), ('Non-Fiction'), ('Fantasy'), ('Sci-Fi'), ('Mystery'), ('Biography');

-- 1 Online (used for loans made through the website), 2 a real librarian
INSERT INTO librarian (full_name, email) VALUES
    ('Online', 'online@library.local'),
    ('Gulnara Seitkali', 'gulnara@library.local');

INSERT INTO publisher (name, country) VALUES
    ('Penguin Books', 'United Kingdom'),       -- 1
    ('HarperCollins', 'United States'),        -- 2
    ('Bloomsbury', 'United Kingdom'),          -- 3
    ('Secker & Warburg', 'United Kingdom'),    -- 4
    ('Allen & Unwin', 'United Kingdom'),       -- 5
    ('Scribner', 'United States'),             -- 6
    ('Ace Books', 'United States'),            -- 7
    ('Simon & Schuster', 'United States'),     -- 8
    ('Collins Crime Club', 'United Kingdom'),  -- 9
    ('Bantam Books', 'United States');         -- 10

INSERT INTO author (full_name, birth_year, country) VALUES
    ('George Orwell', 1903, 'United Kingdom'),        -- 1
    ('J.R.R. Tolkien', 1892, 'United Kingdom'),       -- 2
    ('J.K. Rowling', 1965, 'United Kingdom'),         -- 3
    ('Frank Herbert', 1920, 'United States'),         -- 4
    ('Isaac Asimov', 1920, 'United States'),          -- 5
    ('Agatha Christie', 1890, 'United Kingdom'),      -- 6
    ('Arthur Conan Doyle', 1859, 'United Kingdom'),   -- 7
    ('Yuval Noah Harari', 1976, 'Israel'),            -- 8
    ('Walter Isaacson', 1952, 'United States'),       -- 9
    ('F. Scott Fitzgerald', 1896, 'United States'),   -- 10
    ('Harper Lee', 1926, 'United States'),            -- 11
    ('Ray Bradbury', 1920, 'United States'),          -- 12
    ('Stephen Hawking', 1942, 'United Kingdom'),      -- 13
    ('Michelle Obama', 1964, 'United States'),        -- 14
    ('Leonard Mlodinow', 1954, 'United States');      -- 15

-- Columns: title, year, isbn, category, publisher, description,
--          is_bestseller, total_copies, available_copies
INSERT INTO book (title, publication_year, isbn, category_id, publisher_id,
                  description, is_bestseller, total_copies, available_copies) VALUES
    ('1984', 1949, '978-0451524935', 1, 4, 'A dystopian novel about total surveillance and Big Brother.', true, 5, 4),                       -- 1
    ('Animal Farm', 1945, '978-0451526342', 1, 4, 'A farm revolution that turns into a new tyranny.', false, 4, 4),                         -- 2
    ('The Hobbit', 1937, '978-0547928227', 3, 5, 'Bilbo Baggins joins dwarves on a quest for a dragon''s treasure.', true, 5, 4),           -- 3
    ('The Fellowship of the Ring', 1954, '978-0547928210', 3, 5, 'Frodo sets out to destroy the One Ring.', false, 3, 3),                  -- 4
    ('The Two Towers', 1954, '978-0547928203', 3, 5, 'The fellowship is broken and the war for Middle-earth begins.', false, 2, 2),        -- 5
    ('The Return of the King', 1955, '978-0547928197', 3, 5, 'The final battle against Sauron.', false, 2, 2),                             -- 6
    ('Harry Potter and the Philosopher''s Stone', 1997, '978-0747532699', 3, 3, 'A boy learns he is a wizard and goes to Hogwarts.', true, 5, 5), -- 7
    ('Harry Potter and the Chamber of Secrets', 1998, '978-0747538493', 3, 3, 'A hidden chamber threatens the students of Hogwarts.', false, 3, 3), -- 8
    ('Dune', 1965, '978-0441172719', 4, 7, 'Paul Atreides on the desert planet Arrakis.', true, 4, 3),                                     -- 9
    ('Dune Messiah', 1969, '978-0593098233', 4, 7, 'Paul rules an empire he cannot control.', false, 2, 2),                                -- 10
    ('Foundation', 1951, '978-0553293357', 4, 2, 'A mathematician plans to shorten a galactic dark age.', false, 3, 3),                     -- 11
    ('I, Robot', 1950, '978-0553382563', 4, 2, 'Short stories built around the Three Laws of Robotics.', false, 3, 3),                      -- 12
    ('Fahrenheit 451', 1953, '978-1451673319', 4, 8, 'A fireman whose job is to burn books.', false, 4, 4),                                -- 13
    ('The Martian Chronicles', 1950, '978-1451678192', 4, 8, 'Stories about the human colonisation of Mars.', false, 2, 2),                -- 14
    ('Murder on the Orient Express', 1934, '978-0062693662', 5, 9, 'Hercule Poirot solves a murder on a snowbound train.', true, 4, 3),    -- 15
    ('And Then There Were None', 1939, '978-0062073488', 5, 9, 'Ten strangers on an island die one by one.', false, 3, 3),                 -- 16
    ('The Murder of Roger Ackroyd', 1926, '978-0062073563', 5, 9, 'A village murder with a famous twist ending.', false, 2, 2),            -- 17
    ('A Study in Scarlet', 1887, '978-0141395487', 5, 1, 'The first case of Sherlock Holmes and Dr Watson.', false, 2, 2),                 -- 18
    ('The Hound of the Baskervilles', 1902, '978-0141199177', 5, 1, 'Holmes investigates a legendary hound on the moors.', false, 3, 2),   -- 19
    ('The Great Gatsby', 1925, '978-0743273565', 1, 6, 'Jay Gatsby and his dream of Daisy Buchanan.', false, 3, 3),                       -- 20
    ('Tender Is the Night', 1934, '978-0684801544', 1, 6, 'A glamorous couple on the French Riviera falls apart.', false, 1, 1),            -- 21
    ('To Kill a Mockingbird', 1960, '978-0061120084', 1, 2, 'A lawyer defends a black man in the American South.', false, 4, 4),          -- 22
    ('Sapiens: A Brief History of Humankind', 2011, '978-0062316097', 2, 2, 'How Homo sapiens came to rule the world.', true, 5, 5),       -- 23
    ('Homo Deus: A Brief History of Tomorrow', 2015, '978-0062464316', 2, 2, 'What may happen to humanity in the future.', false, 3, 3), -- 24
    ('A Brief History of Time', 1988, '978-0553380163', 2, 10, 'Black holes, the Big Bang and the nature of time.', false, 3, 3),        -- 25
    ('The Grand Design', 2010, '978-0553805376', 2, 10, 'Why the universe exists, explained with modern physics.', false, 2, 2),         -- 26
    ('A Briefer History of Time', 2005, '978-0553804362', 2, 10, 'A shorter, simpler version of the classic.', false, 1, 1),             -- 27
    ('Steve Jobs', 2011, '978-1451648539', 6, 8, 'The authorised biography of the Apple co-founder.', false, 3, 3),                       -- 28
    ('Einstein: His Life and Universe', 2007, '978-0743264747', 6, 8, 'The life and ideas of Albert Einstein.', false, 2, 2),            -- 29
    ('Becoming', 2018, '978-1524763138', 6, 1, 'The memoir of former First Lady Michelle Obama.', false, 4, 4);                         -- 30

-- (book_id, author_id); books 26 and 27 have two authors
INSERT INTO book_author (book_id, author_id) VALUES
    (1, 1), (2, 1),
    (3, 2), (4, 2), (5, 2), (6, 2),
    (7, 3), (8, 3),
    (9, 4), (10, 4),
    (11, 5), (12, 5),
    (13, 12), (14, 12),
    (15, 6), (16, 6), (17, 6),
    (18, 7), (19, 7),
    (20, 10), (21, 10),
    (22, 11),
    (23, 8), (24, 8),
    (25, 13), (26, 13), (26, 15), (27, 13), (27, 15),
    (28, 9), (29, 9),
    (30, 14);

-- user_id stays NULL until members get Django logins
INSERT INTO member (full_name, email, birth_year) VALUES
    ('Aruzhan Sadykova', 'aruzhan@example.com', 2004),  -- 1
    ('Daniyar Akhmetov', 'daniyar@example.com', 2003),  -- 2
    ('Madina Omarova', 'madina@example.com', 2005),     -- 3
    ('Timur Bekov', 'timur@example.com', 2002),         -- 4
    ('Alina Kim', 'alina@example.com', 2004);           -- 5

-- Dates are relative to today, so loan 3 is always overdue.
-- Active loans (return_date NULL) match available_copies above.
INSERT INTO loan (book_id, member_id, librarian_id, loan_date, due_date, return_date) VALUES
    (1, 1, 2, current_date - 10, current_date + 4, NULL),                -- 1 active
    (3, 2, 1, current_date - 5, current_date + 9, NULL),                 -- 2 active (online)
    (9, 3, 2, current_date - 40, current_date - 26, NULL),               -- 3 overdue
    (23, 1, 2, current_date - 60, current_date - 46, current_date - 50), -- 4 returned
    (15, 4, 1, current_date - 3, current_date + 11, NULL),               -- 5 active (online)
    (19, 2, 2, current_date - 7, current_date + 7, NULL);                -- 6 active

INSERT INTO reservation (book_id, member_id, status) VALUES
    (3, 5, 'pending'),
    (7, 3, 'fulfilled'),
    (9, 4, 'cancelled');

-- Every (book_id, member_id) pair is unique
INSERT INTO review (book_id, member_id, rating, comment) VALUES
    (1, 1, 5, 'Scary and still relevant.'),
    (1, 2, 4, 'Heavy but important.'),
    (3, 2, 5, 'A perfect adventure.'),
    (3, 3, 5, 'Read it in one weekend.'),
    (7, 1, 5, 'Pure magic.'),
    (7, 4, 4, 'Great start of the series.'),
    (9, 3, 4, 'Slow start, epic ending.'),
    (15, 4, 5, 'Did not guess the killer.'),
    (23, 1, 5, 'Changed how I see history.'),
    (23, 5, 4, 'Interesting ideas, a bit long.'),
    (20, 5, 3, 'Beautiful language, sad story.'),
    (13, 2, 4, 'Short and powerful.');
