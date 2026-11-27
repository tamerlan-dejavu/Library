from django.urls import path

from . import views

# All of these live under /api/ (see config/urls.py)
urlpatterns = [
    path("books/", views.book_list),
    path("books/<int:book_id>/", views.book_detail),
    path("books/<int:book_id>/reviews/", views.add_review),
    path("books/<int:book_id>/borrow/", views.borrow),
    path("filters/", views.filters),
    path("register/", views.register),
    path("login/", views.login_view),
    path("logout/", views.logout_view),
    path("me/", views.me),
]
