"""ASGI entry point (not used now, kept for completeness)."""
import os
import sys

from django.core.asgi import get_asgi_application

# Same as in wsgi.py: put back/ on sys.path when started from the repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
