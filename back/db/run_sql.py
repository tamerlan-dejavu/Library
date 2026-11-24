# Usage (from back/): python db/run_sql.py db/schema.sql
import os
import sys

import psycopg
from dotenv import load_dotenv

load_dotenv()
sql = open(sys.argv[1], encoding="utf-8").read()

# The "with" block commits on success and rolls back on error
with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    cur = conn.execute(sql)
    # A file can hold many statements; print the rows of every SELECT
    while True:
        if cur.description:
            print([col.name for col in cur.description])
            for row in cur.fetchall():
                print(row)
            print()
        if not cur.nextset():
            break

print("OK:", sys.argv[1])
