-- Calls each stored function from procedures.sql once.
-- Run: python db/run_sql.py db/call_functions.sql --out ../docs/sql_results/functions.txt

-- Books rated above the overall average, at least 2 reviews
SELECT * FROM fn_books_above_average_rating(2);

-- Members with overdue loans today
SELECT * FROM fn_members_with_overdue_loans();

-- Fantasy books nobody has borrowed yet
SELECT * FROM fn_unborrowed_books('Fantasy');
