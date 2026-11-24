from django.contrib import admin
from django.urls import path

# Only the admin for now; the frontend is served by WhiteNoise
urlpatterns = [
    path("admin/", admin.site.urls),
]
