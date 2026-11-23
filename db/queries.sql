-- 1. Books per genre (JOIN + GROUP BY)
SELECT c.name AS genre, COUNT(b.book_id) AS books
FROM category c LEFT JOIN book b ON b.category_id = c.category_id
GROUP BY c.name ORDER BY books DESC;

-- 2. Top 5 rated books (JOIN + GROUP BY + ORDER BY/LIMIT)
SELECT b.title, ROUND(AVG(r.rating), 2) AS avg_rating, COUNT(*) AS reviews
FROM book b JOIN review r ON r.book_id = b.book_id
GROUP BY b.title ORDER BY avg_rating DESC, reviews DESC LIMIT 5;

-- 3. Overdue loans: not returned and past the due date
SELECT m.full_name, b.title, l.due_date, current_date - l.due_date AS days_late
FROM loan l JOIN member m ON m.member_id = l.member_id JOIN book b ON b.book_id = l.book_id
WHERE l.return_date IS NULL AND l.due_date < current_date;

-- 4. Number of loans per member, including members with none
SELECT m.full_name, COUNT(l.loan_id) AS loans
FROM member m LEFT JOIN loan l ON l.member_id = m.member_id
GROUP BY m.full_name ORDER BY loans DESC;

-- 5. Books that were never borrowed (subquery)
SELECT title FROM book
WHERE book_id NOT IN (SELECT book_id FROM loan)
ORDER BY title;

-- 6. Authors with more than one book (GROUP BY + HAVING)
SELECT a.full_name, COUNT(*) AS books
FROM author a JOIN book_author ba ON ba.author_id = a.author_id
GROUP BY a.full_name HAVING COUNT(*) > 1 ORDER BY books DESC;

-- 7. Books rated above the average of all reviews (subquery in HAVING)
SELECT b.title, ROUND(AVG(r.rating), 2) AS avg_rating
FROM book b JOIN review r ON r.book_id = b.book_id
GROUP BY b.title HAVING AVG(r.rating) > (SELECT AVG(rating) FROM review);

-- 8. Bestsellers with their publisher and copies on the shelf
SELECT b.title, p.name AS publisher, b.available_copies, b.total_copies
FROM book b JOIN publisher p ON p.publisher_id = b.publisher_id
WHERE b.is_bestseller ORDER BY b.title;
