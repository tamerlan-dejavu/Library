import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# BASE_DIR = back/ (Django code), REPO_DIR = repository root (.env, front/)
BASE_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BASE_DIR.parent

# Read variables from the .env file in the repository root (if it exists)
load_dotenv(REPO_DIR / ".env")



def env_list(name):
    # "a.com, b.com" -> ["a.com", "b.com"]; empty or missing -> []
    return [item.strip() for item in os.getenv(name, "").split(",") if item.strip()]


SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.getenv("DEBUG", "False") == "True"

# Vercel preview/production domains and local runs are always allowed;
# extra hosts (e.g. a custom domain) come from ALLOWED_HOSTS
ALLOWED_HOSTS = [".vercel.app", "localhost", "127.0.0.1"] + env_list("ALLOWED_HOSTS")

# POST requests from these https origins pass the CSRF check
# (extra origins, e.g. "https://books.example.com", from CSRF_TRUSTED_ORIGINS)
CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"] + env_list("CSRF_TRUSTED_ORIGINS")

if not DEBUG:
    # Cookies are sent over https only
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Vercel ends https in front of Django and tells us via this header
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise must come right after SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# Needed only by the built-in admin site (we write no templates ourselves)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Supabase transaction pooler (port 6543): no persistent connections
# and no server-side cursors, because the pooler does not support them
DATABASES = {
    "default": dj_database_url.config(conn_max_age=0),
}
DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Qyzylorda"
USE_I18N = True
USE_TZ = True

# Static files of the admin site. "collectstatic" copies them to STATIC_ROOT
# (Vercel runs it during the build and serves them from its CDN).
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Compressed files with a hash in the name (base.4f2a1c.css), so browsers
# can cache them forever
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# The frontend folder (front/ in the repository root)
FRONTEND_DIR = REPO_DIR / "front"

# WhiteNoise serves the frontend at the site root:
# "/" -> front/index.html, "/catalog.html" -> front/catalog.html
# (config/urls.py has a fallback for hosts where WhiteNoise is not active)
WHITENOISE_ROOT = FRONTEND_DIR
WHITENOISE_INDEX_FILE = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Tests use the existing database and roll everything back (see the file)
TEST_RUNNER = "config.test_runner.ExistingDatabaseRunner"
