# Proves that the application role (library_app) has exactly the rights
# it needs. Usage (from back/):  python db/check_app_user.py
# It connects with DATABASE_URL (must be the library_app user).
# Everything happens inside a transaction that is rolled back at the end,
# so the database is not changed.
import os
import sys

import psycopg
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# For each table: an INSERT that respects all constraints, the column to
# UPDATE, and the primary key column. Rows reference existing rows (MIN id).
TABLES = {
    "category": ("INSERT INTO category (name) VALUES ('zz check')", "name", "category_id"),
    "publisher": ("INSERT INTO publisher (name) VALUES ('zz check')", "country", "publisher_id"),
    "author": ("INSERT INTO author (full_name) VALUES ('zz check')", "country", "author_id"),
    "book": ("INSERT INTO book (title, total_copies, available_copies) VALUES ('zz check', 1, 1)",
             "title", "book_id"),
    "book_author": ("INSERT INTO book_author (book_id, author_id) VALUES "
                    "((SELECT min(book_id) FROM book), (SELECT max(author_id) FROM author))",
                    "author_id", "book_author_id"),
    "member": ("INSERT INTO member (full_name) VALUES ('zz check')", "city", "member_id"),
    "member_phone": ("INSERT INTO member_phone (member_id, phone) VALUES "
                     "((SELECT max(member_id) FROM member), '+77000000000')", "phone", "member_phone_id"),
    "librarian": ("INSERT INTO librarian (full_name) VALUES ('zz check')", "full_name", "librarian_id"),
    "loan": ("INSERT INTO loan (book_id, member_id, due_date) VALUES "
             "((SELECT max(book_id) FROM book), (SELECT max(member_id) FROM member), current_date + 14)",
             "due_date", "loan_id"),
    "reservation": ("INSERT INTO reservation (book_id, member_id) VALUES "
                    "((SELECT max(book_id) FROM book), (SELECT max(member_id) FROM member))",
                    "status", "reservation_id"),
    "review": ("INSERT INTO review (book_id, member_id, rating) VALUES "
               "((SELECT max(book_id) FROM book), (SELECT max(member_id) FROM member), 5)",
               "rating", "review_id"),
}

# A value for the UPDATE of each column above (must pass the CHECKs)
NEW_VALUES = {"name": "'zz check 2'", "country": "'Test'", "title": "'zz check 2'",
              "author_id": "author_id", "city": "'Test'", "phone": "'+77000000001'",
              "full_name": "'zz check 2'", "due_date": "due_date + 1",
              "status": "'cancelled'", "rating": "4"}

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail else ""))


def must_fail(conn, name, sql):
    # The statement must be refused with "permission denied" (SQLSTATE 42501)
    try:
        with conn.transaction():          # a savepoint, so we can go on afterwards
            conn.execute(sql)
    except psycopg.errors.InsufficientPrivilege as err:
        check(name, True, str(err).splitlines()[0])
        return
    except psycopg.Error as err:
        check(name, False, "other error: " + str(err).splitlines()[0])
        return
    check(name, False, "it worked, but it should not")


with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    user = conn.execute("SELECT current_user").fetchone()[0]
    print("Connected as:", user)
    check("not the postgres user", user == "library_app", user)

    conn.execute("BEGIN")  # one outer transaction, rolled back at the end
    for table, (insert_sql, column, key) in TABLES.items():
        try:
            with conn.transaction():
                count = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                new_id = conn.execute(insert_sql + f" RETURNING {key}").fetchone()[0]
                updated = conn.execute(
                    f"UPDATE {table} SET {column} = {NEW_VALUES[column]} WHERE {key} = %s", [new_id]
                ).rowcount
                deleted = conn.execute(f"DELETE FROM {table} WHERE {key} = %s", [new_id]).rowcount
            check(f"{table}: SELECT/INSERT/UPDATE/DELETE", updated == 1 and deleted == 1,
                  f"{count} rows visible")
        except psycopg.Error as err:
            check(f"{table}: SELECT/INSERT/UPDATE/DELETE", False, str(err).splitlines()[0])

    must_fail(conn, "DROP TABLE book is refused", "DROP TABLE book")
    must_fail(conn, "CREATE TABLE x is refused", "CREATE TABLE x (id INT)")
    must_fail(conn, "TRUNCATE review is refused", "TRUNCATE review")
    conn.execute("ROLLBACK")

print(f"\n{sum(results)} of {len(results)} checks passed")
sys.exit(0 if all(results) else 1)
