# Runs a .sql file against the database.
# Usage (from back/):
#   python db/run_sql.py db/schema.sql
#   python db/run_sql.py db/queries.sql --out ../docs/sql_results/queries.txt
# Connection: ADMIN_DATABASE_URL if it is set, else DATABASE_URL.
# The URL (and its password) is never printed.
import argparse
import os
import re
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

load_dotenv()
# The Windows console is not UTF-8 by default; Cyrillic text would crash print()
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def format_table(columns, rows, max_width=60):
    # Rows as a plain text table, e.g.
    #   title | year
    #   ------+-----
    #   Dune  | 1965
    def cell(value):
        text = "NULL" if value is None else str(value)
        text = text.replace("\n", " ")
        return text if len(text) <= max_width else text[:max_width - 3] + "..."

    cells = [[cell(v) for v in row] for row in rows]
    widths = [len(c) for c in columns]
    for row in cells:
        widths = [max(w, len(v)) for w, v in zip(widths, row)]

    lines = [" | ".join(c.ljust(w) for c, w in zip(columns, widths)).rstrip(),
             "-+-".join("-" * w for w in widths)]
    for row in cells:
        lines.append(" | ".join(v.ljust(w) for v, w in zip(row, widths)).rstrip())
    lines.append(f"({len(rows)} rows)")
    return "\n".join(lines)


def split_statements(sql):
    # Splits a file at ";" that ends a line, and keeps the "--" comment lines
    # written above each statement as its title. Good enough for our query
    # files; files with function bodies ($$ ... $$) are run as one piece.
    statements = []
    for chunk in re.split(r";[ \t]*\n", sql + "\n"):
        lines = chunk.strip().splitlines()
        title = [l for l in lines if l.startswith("--") and l.strip("- =")]
        code = "\n".join(l for l in lines if not l.startswith("--")).strip()
        if code:
            statements.append(("\n".join(title), code))
    return statements


def main():
    parser = argparse.ArgumentParser(description="Run a .sql file")
    parser.add_argument("file", help="the .sql file to run")
    parser.add_argument("--out", help="also save SELECT results to this text file")
    args = parser.parse_args()

    sql = Path(args.file).read_text(encoding="utf-8")
    url = os.environ.get("ADMIN_DATABASE_URL") or os.environ["DATABASE_URL"]
    report = []

    # The "with" block commits on success and rolls back on error
    with psycopg.connect(url) as conn:
        if args.out:
            # One statement at a time, so every result gets its comment as a title
            for title, code in split_statements(sql):
                cur = conn.execute(code)
                if cur.description:
                    table = format_table([c.name for c in cur.description], cur.fetchall())
                    report.append(f"{title}\n{table}\n")
        else:
            # The whole file at once (works for $$ function bodies too)
            cur = conn.execute(sql)
            while True:
                if cur.description:
                    report.append(format_table([c.name for c in cur.description], cur.fetchall()) + "\n")
                if not cur.nextset():
                    break

    text = "\n".join(report)
    print(text)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f"Results of {Path(args.file).name}\n\n" + text, encoding="utf-8")
        print("Saved:", out)
    print("OK:", args.file)


if __name__ == "__main__":
    main()
