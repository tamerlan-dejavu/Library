# API tests: one happy path and one error case per endpoint.
# Run from back/:  python manage.py test
# They run on the real database with the data from db/seed.sql, but every
# change is rolled back (see config/test_runner.py).
import json

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Book, Loan, Member, Reservation, Review


class ApiTests(TestCase):
    # TestCase wraps the class and every test in a transaction that is
    # rolled back, so tests cannot affect each other or the real data
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="reader", password="secret123")
        cls.member = Member.objects.create(user=cls.user, full_name="reader", birth_year=2000)

    def post_json(self, url, data):
        return self.client.post(url, json.dumps(data), content_type="application/json")

    def log_in(self):
        self.client.login(username="reader", password="secret123")

    # --- GET /api/books/ ---
    def test_books_filter_by_genre(self):
        r = self.client.get("/api/books/?genre=fantasy&genre=MYSTERY")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data["books"]), 11)  # 6 fantasy + 5 mystery
        self.assertEqual({b["genre"] for b in data["books"]}, {"Fantasy", "Mystery"})
        self.assertEqual((data["page"], data["pages"]), (1, 1))

    def test_books_bad_year(self):
        r = self.client.get("/api/books/?year_from=abc")
        self.assertEqual(r.status_code, 400)
        self.assertIn("error", r.json())

    # --- GET /api/books/<id>/ ---
    def test_book_detail(self):
        r = self.client.get("/api/books/1/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["title"], "1984")
        self.assertEqual(data["authors"], ["George Orwell"])
        self.assertEqual(data["rating"], 4.5)
        self.assertEqual(len(data["reviews"]), 2)

    def test_book_detail_not_found(self):
        r = self.client.get("/api/books/999/")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {"error": "Book not found"})

    # --- POST /api/register/ ---
    def test_register(self):
        r = self.post_json("/api/register/", {
            "username": "newbie", "password": "pass1",
            "confirm_password": "pass1", "birth_year": 2000,
        })
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Member.objects.filter(user__username="newbie").exists())
        # The new user is already logged in
        self.assertTrue(self.client.get("/api/me/").json()["logged_in"])

    def test_register_too_young(self):
        r = self.post_json("/api/register/", {
            "username": "kid", "password": "pass1",
            "confirm_password": "pass1", "birth_year": 2015,
        })
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "You must be older than 18.")

    # --- POST /api/login/ ---
    def test_login(self):
        r = self.post_json("/api/login/", {"username": "reader", "password": "secret123"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["username"], "reader")

    def test_login_wrong_password(self):
        r = self.post_json("/api/login/", {"username": "reader", "password": "nope"})
        self.assertEqual(r.status_code, 401)

    # --- POST /api/logout/ ---
    def test_logout(self):
        self.log_in()
        r = self.client.post("/api/logout/")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(self.client.get("/api/me/").json()["logged_in"])

    def test_logout_wrong_method(self):
        r = self.client.get("/api/logout/")
        self.assertEqual(r.status_code, 405)

    # --- GET /api/me/ ---
    def test_me_logged_in(self):
        Loan.objects.create(book_id=2, member=self.member, due_date="2099-01-01")
        self.log_in()
        r = self.client.get("/api/me/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["username"], "reader")
        self.assertEqual(data["loans"][0]["title"], "Animal Farm")
        self.assertIn("csrftoken", r.cookies)

    def test_me_wrong_method(self):
        r = self.client.post("/api/me/")
        self.assertEqual(r.status_code, 405)

    # --- POST /api/books/<id>/reviews/ ---
    def test_add_review(self):
        self.log_in()
        r = self.post_json("/api/books/2/reviews/", {"rating": 5, "comment": "Great"})
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Review.objects.filter(book_id=2, member=self.member).exists())

    def test_add_review_twice(self):
        self.log_in()
        self.post_json("/api/books/2/reviews/", {"rating": 5, "comment": "Great"})
        r = self.post_json("/api/books/2/reviews/", {"rating": 1, "comment": "Again"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "You have already reviewed this book.")

    def test_add_review_not_logged_in(self):
        r = self.post_json("/api/books/2/reviews/", {"rating": 5})
        self.assertEqual(r.status_code, 401)

    # --- POST /api/books/<id>/borrow/ ---
    def test_borrow(self):
        self.log_in()
        r = self.client.post("/api/books/2/borrow/")
        self.assertEqual(r.json()["result"], "borrowed")
        self.assertEqual(Book.objects.get(book_id=2).available_copies, 3)
        loan = Loan.objects.get(book_id=2, member=self.member)
        self.assertEqual(loan.librarian.full_name, "Online")
        self.assertEqual((loan.due_date - loan.loan_date).days, 14)

    def test_borrow_no_copies_reserves(self):
        Book.objects.filter(book_id=2).update(available_copies=0)
        self.log_in()
        r = self.client.post("/api/books/2/borrow/")
        self.assertEqual(r.json()["result"], "reserved")
        self.assertTrue(
            Reservation.objects.filter(book_id=2, member=self.member, status="pending").exists()
        )

    def test_borrow_not_logged_in(self):
        r = self.client.post("/api/books/2/borrow/")
        self.assertEqual(r.status_code, 401)
