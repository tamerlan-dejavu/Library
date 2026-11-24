# API tests: one happy path and one error case per endpoint.
# Run from back/:  python manage.py test
# They run on the real database with the data from db/seed.sql, but every
# change is rolled back (see config/test_runner.py).
import json
from pathlib import Path

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from .management.commands import import_books
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
        Review.objects.create(book_id=3, member=self.member, rating=4)
        self.log_in()
        r = self.client.get("/api/me/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["username"], "reader")
        self.assertEqual(data["loans"][0]["title"], "Animal Farm")
        self.assertEqual(data["loans"][0]["book_id"], 2)
        self.assertEqual(data["reviews"][0]["book_id"], 3)
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

    def test_borrow_twice(self):
        self.log_in()
        self.client.post("/api/books/2/borrow/")
        r = self.client.post("/api/books/2/borrow/")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "You already have this book.")
        self.assertEqual(Book.objects.get(book_id=2).available_copies, 3)

    def test_reserve_twice(self):
        Book.objects.filter(book_id=2).update(available_copies=0)
        self.log_in()
        self.client.post("/api/books/2/borrow/")
        r = self.client.post("/api/books/2/borrow/")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "You already reserved this book.")
        self.assertEqual(Reservation.objects.filter(book_id=2, member=self.member).count(), 1)

    def test_borrow_not_logged_in(self):
        r = self.client.post("/api/books/2/borrow/")
        self.assertEqual(r.status_code, 401)


# ---------- Open Library import: parsing only, no network, no database ----------

# Real (shortened) answers from Open Library, saved in test_data/
SAMPLE = json.loads(
    (Path(__file__).parent / "test_data" / "openlibrary_sample.json").read_text(encoding="utf-8")
)


class OpenLibraryParsingTests(SimpleTestCase):
    def test_work_id(self):
        key = SAMPLE["search"]["docs"][0]["key"]
        self.assertEqual(key, "/works/OL138052W")
        self.assertEqual(import_books.work_id(key), "OL138052W")

    def test_description_object_string_and_missing(self):
        text = import_books.get_description(SAMPLE["work_with_object_description"])
        self.assertTrue(text.startswith("Alice's Adventures in Wonderland"))
        text = import_books.get_description(SAMPLE["work_with_string_description"])
        self.assertTrue(text.startswith("A reprinting of the 1843"))
        self.assertEqual(import_books.get_description(SAMPLE["work_without_description"]),
                         "No description available.")
        self.assertEqual(import_books.get_description(None), "No description available.")

    def test_shorten_at_sentence_end(self):
        text = "This is one sentence. " * 50  # 1100 characters
        short = import_books.shorten(text)
        self.assertLessEqual(len(short), 600)
        self.assertTrue(short.endswith("."))

    def test_pick_books_skips_incomplete_known_and_repeated(self):
        docs = SAMPLE["search"]["docs"]
        no_cover = dict(docs[0], key="/works/OL9W", title="No cover")
        del no_cover["cover_i"]
        all_docs = [no_cover, docs[0], docs[1], dict(docs[0])]  # last one repeats a key

        seen = set()
        titles = {"a christmas carol"}  # already in our table
        picked, skipped = import_books.pick_books(all_docs, seen, titles)

        self.assertEqual([d["title"] for d in picked], ["Alice's Adventures in Wonderland"])
        self.assertEqual(skipped, 3)
        # Running again finds nothing new (safe to run twice)
        picked, skipped = import_books.pick_books(all_docs, seen, titles)
        self.assertEqual(picked, [])

    def test_bestsellers_and_cover_url(self):
        docs = [{"key": "a", "edition_count": 5}, {"key": "b", "edition_count": 50},
                {"key": "c", "edition_count": 20}]
        self.assertEqual(import_books.bestseller_keys(docs), {"b", "c"})
        self.assertEqual(import_books.cover_url(10527843),
                         "https://covers.openlibrary.org/b/id/10527843-L.jpg")
