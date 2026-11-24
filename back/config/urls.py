from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve


def frontend(request, path):
    # Fallback that serves front/ through Django. Normally WhiteNoise answers
    # first; this runs only where WhiteNoise is not active (e.g. on Vercel).
    # serve() refuses paths outside FRONTEND_DIR, like "../.env".
    return serve(request, path or "index.html", document_root=settings.FRONTEND_DIR)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("catalog.urls")),
    # Everything else is a file from front/ ("" -> index.html).
    # (?!admin|api) skips those paths, so "/admin" still redirects to "/admin/"
    re_path(r"^(?!admin|api)(?P<path>.*)$", frontend),
]
