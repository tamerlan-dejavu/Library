from django.contrib import admin
from django.urls import include, path

# The frontend itself is served by WhiteNoise (see settings.py)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("catalog.urls")),
]
