# Book Catalog: a Library Database Project

https://library-kappa-eight.vercel.app/

https://www.figma.com/design/pCMCj7ck0AuD1ufCNWxMaF/First_lab?node-id=0-1&t=HzCb5ytFDVQlfYwq-1

A small online library: readers find, borrow and review books.
Django JSON API + static frontend + PostgreSQL (Supabase, 11 tables).

## Stack

| Part      | Version                                                        |
|-----------|----------------------------------------------------------------|
| Python    | 3.12 (`.python-version`)                                       |
| Django    | 5.2.19                                                         |
| Database  | PostgreSQL on Supabase; psycopg 3.3.9, dj-database-url 3.1.2   |
| Other     | python-dotenv 1.2.4, whitenoise 6.12.0, gunicorn 27.0.1, asgiref 3.13.0, sqlparse 0.6.1, tzdata 2026.6 |
| Frontend  | HTML, CSS, vanilla JavaScript, Bootstrap 5.3.3 (CDN)           |
| Hosting   | Vercel                                                         |

## Folders

```
back/            Django project (manage.py)
back/config/     settings, urls, wsgi
back/catalog/    models, admin, JSON API (views.py), tests.py, management commands
back/db/         SQL scripts, seed generator, run_sql.py, check_app_user.py
front/           HTML pages, css/style.css, js/, assets/, covers/
docs/sql_results/  saved results of the SQL reports
```

## Run locally

```bash
python -m venv venv
venv\Scripts\activate              # macOS / Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env             # macOS / Linux: cp; then fill in your own values
cd back
python manage.py runserver
```

Open http://127.0.0.1:8000/

`.env.example` lists the variables (without values): `DJANGO_SECRET_KEY`, `DEBUG`,
`ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`, `ADMIN_DATABASE_URL`,
`APP_DB_PASSWORD`.

## SQL scripts (run from `back/`)

First `python manage.py migrate` (Django tables), then:

```bash
python db/run_sql.py db/schema.sql            # 1. tables (drops them first)
python db/run_sql.py db/seed.sql              # 2. demo data
python db/run_sql.py db/procedures.sql        # 3. stored functions
python db/run_sql.py db/security.sql          # 4. role library_app and its rights
python db/run_sql.py db/post_seed_covers.sql  # 5. five bestsellers with covers
```

Any time after step 4: `queries.sql`, `structure.sql`, `call_functions.sql`
(add `--out ../docs/sql_results/<name>.txt` to save the results).

## Database roles

- **Admin role** (`ADMIN_DATABASE_URL`): owner of the tables; used only for
  `migrate` and the SQL scripts above (DDL: CREATE, DROP, ALTER).
- **library_app** (`DATABASE_URL`): used by the website, the tests and Vercel.
  It can only read and change rows (SELECT, INSERT, UPDATE, DELETE);
  CREATE, DROP and TRUNCATE are refused.

## Checks (from `back/`)

```bash
python manage.py test          # API, admin, model and SQL function tests
python db/check_app_user.py    # proves what library_app may and may not do
```
