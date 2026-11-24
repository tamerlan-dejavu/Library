# Book Catalog

A student project: an online library where readers browse books, borrow or
reserve them and write reviews. The backend is Django with a small JSON API
and an admin panel. The data lives in PostgreSQL (Supabase). The frontend is
static HTML + Bootstrap + vanilla JS. The book page also shows data from the
public Open Library API.

Links: [design in Figma](https://www.figma.com/design/pCMCj7ck0AuD1ufCNWxMaF/First_lab?node-id=0-1&t=HzCb5ytFDVQlfYwq-1)

## Run locally

```bash
python -m venv venv
venv\Scripts\activate            # Windows (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # then fill in the values (cp on macOS/Linux)

cd back
python manage.py migrate                 # Django tables (auth, sessions, admin)
python db/run_sql.py db/schema.sql       # catalog tables (drops them first!)
python db/run_sql.py db/seed.sql         # demo data
python manage.py import_books            # optional: ~70 real books from Open Library
python manage.py createsuperuser         # login for /admin/
python manage.py runserver               # http://127.0.0.1:8000
```

Set `DEBUG=True` in `.env` on your computer. With `DEBUG=False`, run
`python manage.py collectstatic --noinput` first. Note that login will not work
over plain http then, because cookies are marked secure.

Tests: `python manage.py test` (in `back/`).

## Deploy to Vercel

1. Push the repository to GitHub. In Vercel choose **Add New → Project** and
   import it. Keep the **Root Directory** as the repository root, because the
   function needs both `back/` and `front/`. Vercel finds `back/manage.py` by
   itself.
2. Add the environment variables: `DJANGO_SECRET_KEY`, `DATABASE_URL` and
   `DEBUG=False`. Optional: `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` for a
   custom domain.
3. Click **Deploy**. Vercel installs `requirements.txt`, runs `collectstatic`
   and serves the admin static files from its CDN. Run migrations and the SQL
   scripts once from your computer against the same database.

## Project structure

```
requirements.txt, .python-version   dependencies and Python version (Vercel reads them here)
back/manage.py                      Django entry point
back/config/                        settings, urls (API, admin, frontend fallback), wsgi
back/catalog/models.py, admin.py    10 tables (managed=False) and the admin panel
back/catalog/views.py, urls.py      JSON API under /api/
back/catalog/management/commands/   import_books (Open Library)
back/catalog/tests.py               API tests and import parsing tests
back/db/                            schema.sql, seed.sql, queries.sql, run_sql.py
front/                              static pages, css/style.css, js/, assets/
```
