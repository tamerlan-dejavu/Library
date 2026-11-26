# Book Catalog

A university project: an online library where readers browse books, borrow
or reserve them and write reviews. The backend is Django with a small JSON
API and an admin panel. The data lives in PostgreSQL on Supabase (11
tables, stored functions, a separate application role). The frontend is
static HTML + Bootstrap + vanilla JS. The book page also shows data from the
public Open Library API.

Readers register with first name, last name, e-mail and password and sign in
with their e-mail. The e-mail (in lower case) is also the hidden Django
username, so no separate username is ever shown or typed. E-mails are unique
without letter case (a unique index on `lower(email)` in `member`). Reviews
show only the first name and the first letter of the last name ("Алихан Б.").

Design: [Figma](https://www.figma.com/design/pCMCj7ck0AuD1ufCNWxMaF/First_lab?node-id=0-1&t=HzCb5ytFDVQlfYwq-1)

## Technologies

| Part      | Technology and version                                                |
|-----------|-----------------------------------------------------------------------|
| Language  | Python 3.12 on Vercel (`.python-version`); 3.12-3.14 work locally     |
| Backend   | Django 5.2.19, psycopg 3.3.9, dj-database-url 3.1.2, python-dotenv 1.2.4 |
| Static    | WhiteNoise 6.12.0 (gunicorn 27.0.1 for a classic server)              |
| Database  | PostgreSQL 17 on Supabase, transaction pooler (port 6543), UTF8       |
| Frontend  | HTML, CSS, vanilla JavaScript, Bootstrap 5.3.3 (CDN), Google Fonts    |
| External  | Open Library API (no key)                                             |
| Hosting   | Vercel (Python runtime)                                               |

## Two database users

| Variable             | User                          | Used for                                              |
|----------------------|-------------------------------|-------------------------------------------------------|
| `ADMIN_DATABASE_URL` | `postgres.<project_ref>`      | `python manage.py migrate` and all `db/*.sql` scripts |
| `DATABASE_URL`       | `library_app.<project_ref>`   | runserver, tests, `import_books`, Vercel              |

`library_app` (created by `db/security.sql`) can only read and change rows:
no CREATE, DROP, TRUNCATE or ALTER. `settings.py` always reads
`DATABASE_URL`; `db/run_sql.py` uses `ADMIN_DATABASE_URL` when it is set.

Connection string for the application (Supabase transaction pooler). Take
`<project_ref>` and the host from your `postgres.<project_ref>` admin URL:

```
DATABASE_URL=postgresql://library_app.<project_ref>:<APP_DB_PASSWORD>@aws-1-<region>.pooler.supabase.com:6543/postgres
```

Special characters in a password must be %-encoded in the URL
(for example `[` becomes `%5B`).

## Run locally

```bash
python -m venv venv
venv\Scripts\activate            # Windows (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # fill in the values (cp on macOS/Linux)
cd back
```

Set up the database once, as the admin user, in this order:

```powershell
# PowerShell: run migrate with the admin connection
$env:DATABASE_URL = (Select-String '^ADMIN_DATABASE_URL=' ..\.env).Line.Split('=', 2)[1]
python manage.py migrate
Remove-Item Env:DATABASE_URL      # back to the library_app URL from .env
```

```bash
# bash: the same for one command only
DATABASE_URL="$(grep '^ADMIN_DATABASE_URL=' ../.env | cut -d= -f2-)" python manage.py migrate
```

```bash
python db/run_sql.py db/schema.sql       # 1. tables (drops them first!)
python db/run_sql.py db/seed.sql         # 2. demo data
python db/run_sql.py db/procedures.sql   # 3. stored functions
python db/run_sql.py db/security.sql     # 4. role library_app (needs APP_DB_PASSWORD)
python db/check_app_user.py              # check the rights of library_app
python manage.py import_books            # optional: extra books from Open Library
python manage.py createsuperuser         # login for /admin/
python manage.py runserver               # http://127.0.0.1:8000
python manage.py test                    # tests (as library_app)
```

### Book covers: copy them into the project

`import_books` stores Open Library cover links. That server is often slow,
so the covers can be copied into `front/covers/` and served by our own site:

1. `python manage.py download_covers` downloads the medium cover of each
   book to `front/covers/<book_id>.jpg` (slow and polite: 1 request per
   second, 3 tries, skips files that already exist). Run it again for the
   books listed as failed.
2. Commit `front/covers/` and deploy, so the images are online.
3. `python manage.py download_covers --update-db` sets `cover_url` to
   `covers/<book_id>.jpg` for every book that has a file.

The order matters: the live site reads `cover_url` from the same database,
so the database may point to `covers/...` only after those files are
deployed; otherwise visitors would get missing images in between. Books
without a downloaded file keep their Open Library link.

After `schema.sql` run `security.sql` again: dropped and re-created tables
need their row level security policy again.

Set `DEBUG=True` in `.env` on your computer. With `DEBUG=False`, run
`python manage.py collectstatic --noinput` first; login then needs https.

SQL reports (saved in `docs/sql_results/`):

```bash
python db/run_sql.py db/structure.sql --out ../docs/sql_results/structure.txt
python db/run_sql.py db/queries.sql --out ../docs/sql_results/queries.txt
python db/run_sql.py db/call_functions.sql --out ../docs/sql_results/functions.txt
```

## Files in back/db/

| File                 | What it does                                                          |
|----------------------|-----------------------------------------------------------------------|
| `schema.sql`         | Creates the 11 tables, constraints and indexes; ER mapping in the header |
| `generate_seed.py`   | Writes `seed.sql` (fixed random seed, no network)                     |
| `seed.sql`           | Demo data: 143 real books, 134 authors, 125 members, 180 loans, ...   |
| `procedures.sql`     | Three PL/pgSQL functions (above-average books, overdue members, unborrowed books) |
| `security.sql`       | Role `library_app`, grants, row level security policies              |
| `structure.sql`      | Report: columns, constraints, row counts and indexes of the 11 tables |
| `queries.sql`        | Demonstration queries: joins, aggregates, subqueries                  |
| `call_functions.sql` | Calls each stored function once                                       |
| `run_sql.py`         | Runs a .sql file; `--out` saves the results as text tables            |
| `check_app_user.py`  | Proves what `library_app` may and may not do (rolled back)            |

## Deploy to Vercel

1. Push the repository to GitHub. In Vercel choose **Add New → Project** and
   import it. Keep the **Root Directory** as the repository root (the
   function needs both `back/` and `front/`); Vercel finds `back/manage.py`.
2. Environment variables: `DJANGO_SECRET_KEY`, `DATABASE_URL` (the
   **library_app** URL) and `DEBUG=False`. Optional: `ALLOWED_HOSTS` and
   `CSRF_TRUSTED_ORIGINS` for a custom domain. Do not give Vercel the admin URL.
3. Click **Deploy**. Vercel installs `requirements.txt`, runs `collectstatic`
   and serves the admin static files from its CDN. Database setup is done
   from your computer (see above).

## Project structure

```
requirements.txt, .python-version   dependencies and Python version (Vercel reads them here)
back/manage.py                      Django entry point
back/config/                        settings, urls (API, admin, frontend fallback), wsgi
back/catalog/models.py, admin.py    11 tables (managed=False) and the admin panel
back/catalog/views.py, urls.py      JSON API under /api/
back/catalog/management/commands/   import_books (Open Library), download_covers
back/catalog/tests.py               API, admin, model rule and stored function tests
back/db/                            SQL scripts and helpers (see the table above)
docs/sql_results/                   saved results of the SQL reports
front/                              static pages, css/style.css, js/, assets/, covers/
```
