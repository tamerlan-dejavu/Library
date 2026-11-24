# Tests. Run from back/:  python manage.py test
# They run on the real database but every change is rolled back
# (see config/test_runner.py). Each test class creates the rows it needs,
# so the tests do not depend on the data from db/seed.sql.
import json
import tempfile
from datetime import timedelta
from pathlib import Path

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from .management.commands import download_covers, import_books
from .models import (
    Author, Book, BookAuthor, Category, Librarian, Loan, Member,
    MemberPhone, Publisher, Reservation, Review,
)

# Every test title starts with this word, so searches find only our books
TAG = "Zzqx"


class CatalogTestData(TestCase):
    # TestCase wraps the class and every test in a transaction that is
    # rolled back, so tests cannot affect each other or the real data
    @classmethod
    def setUpTestData(cls):
        cls.alpha = Category.objects.create(name="Test Genre Alpha")
        cls.beta = Category.objects.create(name="Test Genre Beta")
        publisher = Publisher.objects.create(name="Test Publisher")
        cls.author1 = Author.objects.create(full_name="Test Author One")
        cls.author2 = Author.objects.create(full_name="Test Author Two")

        cls.book1 = Book.objects.create(
            title=f"{TAG} Book One", category=cls.alpha, publisher=publisher,
            publication_year=1950, is_bestseller=True, total_copies=4, available_copies=4,
        )
        cls.book2 = Book.objects.create(
            title=f"{TAG} Book Two", category=cls.beta, publisher=publisher,
            publication_year=2001, total_copies=2, available_copies=2,
        )
        cls.book3 = Book.objects.create(
            title=f"{TAG} Book Three", category=cls.alpha, publisher=publisher,
            publication_year=2010, total_copies=1, available_copies=1,
        )
        BookAuthor.objects.create(book=cls.book1, author=cls.author1)
        BookAuthor.objects.create(book=cls.book2, author=cls.author2)
        BookAuthor.objects.create(book=cls.book3, author=cls.author1)

        cls.user = User.objects.create_user(username="zzqx_reader", password="secret123")
        cls.member = Member.objects.create(user=cls.user, full_name="zzqx reader", birth_year=2000)
        cls.other1 = Member.objects.create(full_name="Zzqx Other One", birth_year=1990)
        cls.other2 = Member.objects.create(full_name="Zzqx Other Two", birth_year=1985)

        # book1: two 5-star reviews; book3: one 1-star review
        Review.objects.create(book=cls.book1, member=cls.other1, rating=5, comment="Great")
        Review.objects.create(book=cls.book1, member=cls.other2, rating=5, comment="Super")
        Review.objects.create(book=cls.book3, member=cls.other1, rating=1, comment="Bad")

        # The borrow view needs the "Online" librarian
        Librarian.objects.get_or_create(full_name="Online", defaults={"email": "zzqx-online@library.local"})

    def post_json(self, url, data):
        return self.client.post(url, json.dumps(data), content_type="application/json")

    def log_in(self):
        self.client.login(username="zzqx_reader", password="secret123")


class ApiTests(CatalogTestData):
    # --- GET /api/books/ ---
    def test_books_filter_by_genre(self):
        r = self.client.get("/api/books/?genre=test genre alpha&genre=TEST GENRE BETA")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data["books"]), 3)
        self.assertEqual({b["genre"] for b in data["books"]}, {"Test Genre Alpha", "Test Genre Beta"})
        self.assertEqual((data["page"], data["pages"]), (1, 1))

    def test_books_search_and_bestseller(self):
        r = self.client.get("/api/books/?q=test author two")
        self.assertEqual([b["title"] for b in r.json()["books"]], [f"{TAG} Book Two"])
        r = self.client.get(f"/api/books/?q={TAG}&bestseller=1&year_from=1940&year_to=1960")
        self.assertEqual([b["title"] for b in r.json()["books"]], [f"{TAG} Book One"])

    def test_books_bad_year(self):
        r = self.client.get("/api/books/?year_from=abc")
        self.assertEqual(r.status_code, 400)
        self.assertIn("error", r.json())

    # --- GET /api/books/<id>/ ---
    def test_book_detail(self):
        r = self.client.get(f"/api/books/{self.book1.book_id}/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["title"], f"{TAG} Book One")
        self.assertEqual(data["authors"], ["Test Author One"])
        self.assertEqual(data["rating"], 5.0)
        self.assertEqual(len(data["reviews"]), 2)

    def test_book_detail_not_found(self):
        missing_id = Book.objects.order_by("-book_id").first().book_id + 1000
        r = self.client.get(f"/api/books/{missing_id}/")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {"error": "Book not found"})

    # --- POST /api/register/ ---
    def test_register(self):
        r = self.post_json("/api/register/", {
            "username": "zzqx_newbie", "password": "pass1",
            "confirm_password": "pass1", "birth_year": 2000,
        })
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Member.objects.filter(user__username="zzqx_newbie").exists())
        # The new user is already logged in
        self.assertTrue(self.client.get("/api/me/").json()["logged_in"])

    def test_register_too_young(self):
        r = self.post_json("/api/register/", {
            "username": "zzqx_kid", "password": "pass1",
            "confirm_password": "pass1", "birth_year": timezone.localdate().year - 10,
        })
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "You must be older than 18.")

    # --- POST /api/login/ ---
    def test_login(self):
        r = self.post_json("/api/login/", {"username": "zzqx_reader", "password": "secret123"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["username"], "zzqx_reader")

    def test_login_wrong_password(self):
        r = self.post_json("/api/login/", {"username": "zzqx_reader", "password": "nope"})
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
        Loan.objects.create(book=self.book2, member=self.member, due_date="2099-01-01")
        Review.objects.create(book=self.book3, member=self.member, rating=4)
        self.log_in()
        r = self.client.get("/api/me/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["username"], "zzqx_reader")
        self.assertEqual(data["loans"][0]["title"], f"{TAG} Book Two")
        self.assertEqual(data["loans"][0]["book_id"], self.book2.book_id)
        self.assertEqual(data["reviews"][0]["book_id"], self.book3.book_id)
        self.assertIn("csrftoken", r.cookies)

    def test_me_wrong_method(self):
        r = self.client.post("/api/me/")
        self.assertEqual(r.status_code, 405)

    # --- POST /api/books/<id>/reviews/ ---
    def test_add_review(self):
        self.log_in()
        r = self.post_json(f"/api/books/{self.book2.book_id}/reviews/", {"rating": 5, "comment": "Great"})
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Review.objects.filter(book=self.book2, member=self.member).exists())

    def test_add_review_twice(self):
        self.log_in()
        url = f"/api/books/{self.book2.book_id}/reviews/"
        self.post_json(url, {"rating": 5, "comment": "Great"})
        r = self.post_json(url, {"rating": 1, "comment": "Again"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "You have already reviewed this book.")

    def test_add_review_not_logged_in(self):
        r = self.post_json(f"/api/books/{self.book2.book_id}/reviews/", {"rating": 5})
        self.assertEqual(r.status_code, 401)

    # --- POST /api/books/<id>/borrow/ ---
    def test_borrow(self):
        self.log_in()
        r = self.client.post(f"/api/books/{self.book2.book_id}/borrow/")
        self.assertEqual(r.json()["result"], "borrowed")
        self.assertEqual(Book.objects.get(pk=self.book2.pk).available_copies, 1)
        loan = Loan.objects.get(book=self.book2, member=self.member)
        self.assertEqual(loan.librarian.full_name, "Online")
        self.assertEqual((loan.due_date - loan.loan_date).days, 14)

    def test_borrow_no_copies_reserves(self):
        Book.objects.filter(pk=self.book2.pk).update(available_copies=0)
        self.log_in()
        r = self.client.post(f"/api/books/{self.book2.book_id}/borrow/")
        self.assertEqual(r.json()["result"], "reserved")
        self.assertTrue(
            Reservation.objects.filter(book=self.book2, member=self.member, status="pending").exists()
        )

    def test_borrow_twice(self):
        self.log_in()
        url = f"/api/books/{self.book2.book_id}/borrow/"
        self.client.post(url)
        r = self.client.post(url)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "You already have this book.")
        self.assertEqual(Book.objects.get(pk=self.book2.pk).available_copies, 1)

    def test_reserve_twice(self):
        Book.objects.filter(pk=self.book2.pk).update(available_copies=0)
        self.log_in()
        url = f"/api/books/{self.book2.book_id}/borrow/"
        self.client.post(url)
        r = self.client.post(url)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "You already reserved this book.")
        self.assertEqual(Reservation.objects.filter(book=self.book2, member=self.member).count(), 1)

    def test_borrow_not_logged_in(self):
        r = self.client.post(f"/api/books/{self.book2.book_id}/borrow/")
        self.assertEqual(r.status_code, 401)


class ModelRuleTests(CatalogTestData):
    # full_clean() runs the same checks as an admin form

    def test_review_rating_must_be_1_to_5(self):
        review = Review(book=self.book2, member=self.member, rating=6)
        with self.assertRaises(ValidationError) as ctx:
            review.full_clean()
        self.assertIn("rating", ctx.exception.message_dict)

    def test_available_copies_not_more_than_total(self):
        book = Book(title=f"{TAG} Bad", total_copies=1, available_copies=2)
        with self.assertRaises(ValidationError) as ctx:
            book.full_clean()
        self.assertIn("available_copies", ctx.exception.message_dict)

    def test_due_date_not_before_loan_date(self):
        today = timezone.localdate()
        loan = Loan(book=self.book2, member=self.member, loan_date=today, due_date=today - timedelta(days=1))
        with self.assertRaises(ValidationError) as ctx:
            loan.full_clean()
        self.assertIn("due_date", ctx.exception.message_dict)

    def test_member_phone_format(self):
        phone = MemberPhone(member=self.member, phone="12-ab")
        with self.assertRaises(ValidationError) as ctx:
            phone.full_clean()
        self.assertIn("phone", ctx.exception.message_dict)

    def test_member_phone_unique_per_member(self):
        MemberPhone.objects.create(member=self.member, phone="+77011234567")
        with self.assertRaises(ValidationError):
            MemberPhone(member=self.member, phone="+77011234567").full_clean()

    def test_member_birth_year_range(self):
        with self.assertRaises(ValidationError) as ctx:
            Member(full_name="Zzqx Old", birth_year=1850).full_clean()
        self.assertIn("birth_year", ctx.exception.message_dict)

    # The database CHECKs work even when Django validation is skipped
    def test_database_rejects_bad_phone_and_birth_year(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MemberPhone.objects.create(member=self.member, phone="not a phone")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Member.objects.create(full_name="Zzqx Young", birth_year=2015)

    def test_phones_are_deleted_with_member(self):
        member = Member.objects.create(full_name="Zzqx Temp")
        MemberPhone.objects.create(member=member, phone="+77019998877")
        member.delete()
        self.assertFalse(MemberPhone.objects.filter(phone="+77019998877").exists())


class StoredFunctionTests(CatalogTestData):
    # The functions come from db/procedures.sql

    def call(self, sql, params):
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def test_books_above_average_rating(self):
        rows = self.call("SELECT book_id, review_count FROM fn_books_above_average_rating(%s)", [2])
        self.assertIn((self.book1.book_id, 2), rows)       # 5.0 is above the average
        self.assertNotIn(self.book3.book_id, [r[0] for r in rows])

    def test_members_with_overdue_loans(self):
        Loan.objects.create(book=self.book1, member=self.other1,
                            loan_date=timezone.localdate() - timedelta(days=24),
                            due_date=timezone.localdate() - timedelta(days=10))
        rows = self.call("SELECT member_id, overdue_loans, max_days_overdue "
                         "FROM fn_members_with_overdue_loans()", [])
        row = [r for r in rows if r[0] == self.other1.member_id][0]
        self.assertEqual(row[1], 1)
        self.assertGreaterEqual(row[2], 9)  # 10 days; 9 or 11 near midnight UTC

    def test_unborrowed_books_by_genre(self):
        Loan.objects.create(book=self.book1, member=self.other1, due_date="2099-01-01")
        rows = self.call("SELECT title FROM fn_unborrowed_books(%s)", ["test genre alpha"])
        self.assertEqual(rows, [(f"{TAG} Book Three",)])


# Admin pages need static file URLs; the simple storage works without
# running collectstatic first
@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class AdminTests(CatalogTestData):
    # Create, update and delete through the admin, and clear error messages

    def setUp(self):
        admin_user = User.objects.create_superuser("zzqx_admin", "zzqx@example.com", "pw")
        self.client.force_login(admin_user)
        self.today = timezone.localdate()

    def book_form(self, **changes):
        data = {"title": f"{TAG} Admin Book", "publication_year": "2020", "isbn": "",
                "category": self.alpha.pk, "publisher": "", "description": "", "cover_url": "",
                "total_copies": "3", "available_copies": "3"}
        data.update(changes)
        return data

    def member_form(self, **changes):
        # The phone inline needs Django's "management form" fields
        data = {"full_name": "Zzqx Admin Member", "email": "", "birth_year": "1999",
                "city": "Алматы", "street": "Абай даңғылы, 1", "user": "",
                "memberphone_set-TOTAL_FORMS": "1", "memberphone_set-INITIAL_FORMS": "0",
                "memberphone_set-MIN_NUM_FORMS": "0", "memberphone_set-MAX_NUM_FORMS": "1000",
                "memberphone_set-0-phone": "+77010000001"}
        data.update(changes)
        return data

    def loan_form(self, **changes):
        data = {"book": self.book2.pk, "member": self.other1.pk, "librarian": "",
                "loan_date": str(self.today), "due_date": str(self.today + timedelta(days=14)),
                "return_date": ""}
        data.update(changes)
        return data

    def test_book_create_update_delete(self):
        r = self.client.post("/admin/catalog/book/add/", self.book_form())
        self.assertEqual(r.status_code, 302)  # redirect = saved
        book = Book.objects.get(title=f"{TAG} Admin Book")

        r = self.client.post(f"/admin/catalog/book/{book.pk}/change/", self.book_form(total_copies="5"))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Book.objects.get(pk=book.pk).total_copies, 5)

        r = self.client.post(f"/admin/catalog/book/{book.pk}/delete/", {"post": "yes"})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Book.objects.filter(pk=book.pk).exists())

    def test_member_create_update_delete(self):
        r = self.client.post("/admin/catalog/member/add/", self.member_form())
        self.assertEqual(r.status_code, 302)
        member = Member.objects.get(full_name="Zzqx Admin Member")
        self.assertEqual(member.memberphone_set.get().phone, "+77010000001")
        self.assertIsNotNone(member.registered_at)  # filled by DEFAULT now()

        r = self.client.post(f"/admin/catalog/member/{member.pk}/change/",
                             self.member_form(city="Астана", **{"memberphone_set-TOTAL_FORMS": "0"}))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Member.objects.get(pk=member.pk).city, "Астана")

        r = self.client.post(f"/admin/catalog/member/{member.pk}/delete/", {"post": "yes"})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Member.objects.filter(pk=member.pk).exists())
        self.assertFalse(MemberPhone.objects.filter(phone="+77010000001").exists())

    def test_loan_create_update_delete(self):
        r = self.client.post("/admin/catalog/loan/add/", self.loan_form())
        self.assertEqual(r.status_code, 302)
        loan = Loan.objects.get(book=self.book2, member=self.other1)

        r = self.client.post(f"/admin/catalog/loan/{loan.pk}/change/",
                             self.loan_form(return_date=str(self.today)))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Loan.objects.get(pk=loan.pk).return_date, self.today)

        r = self.client.post(f"/admin/catalog/loan/{loan.pk}/delete/", {"post": "yes"})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Loan.objects.filter(pk=loan.pk).exists())

    def test_duplicate_review_message(self):
        # other1 already reviewed book1 (see setUpTestData)
        r = self.client.post("/admin/catalog/review/add/",
                             {"book": self.book1.pk, "member": self.other1.pk, "rating": "4", "comment": ""})
        self.assertEqual(r.status_code, 200)  # the form is shown again with an error
        self.assertContains(r, "Review with this Book and Member already exists.")

    def test_rating_9_message(self):
        r = self.client.post("/admin/catalog/review/add/",
                             {"book": self.book2.pk, "member": self.member.pk, "rating": "9", "comment": ""})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Ensure this value is less than or equal to 5.")

    def test_due_date_before_loan_date_message(self):
        r = self.client.post("/admin/catalog/loan/add/",
                             self.loan_form(due_date=str(self.today - timedelta(days=3))))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Due date cannot be before the loan date.")

    def test_delete_member_with_loans_is_refused(self):
        Loan.objects.create(book=self.book2, member=self.other2, due_date=self.today + timedelta(days=7))
        r = self.client.post(f"/admin/catalog/member/{self.other2.pk}/delete/", {"post": "yes"})
        self.assertEqual(r.status_code, 200)  # not deleted, a page explains why
        self.assertContains(r, "would require deleting the following protected related objects")
        self.assertTrue(Member.objects.filter(pk=self.other2.pk).exists())

    def test_admin_title(self):
        r = self.client.get("/admin/")
        self.assertContains(r, "Book Catalog administration")


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


# ---------- download_covers: URL and path logic, no network ----------

class CoverPathTests(SimpleTestCase):
    def test_only_open_library_covers_are_downloaded(self):
        self.assertTrue(download_covers.is_open_library_cover(
            "https://covers.openlibrary.org/b/id/10527843-L.jpg"))
        self.assertFalse(download_covers.is_open_library_cover("covers/7.jpg"))
        self.assertFalse(download_covers.is_open_library_cover(None))

    def test_medium_url(self):
        self.assertEqual(
            download_covers.medium_url("https://covers.openlibrary.org/b/id/10527843-L.jpg"),
            "https://covers.openlibrary.org/b/id/10527843-M.jpg")

    def test_file_path_and_database_value(self):
        folder = Path("front") / "covers"
        self.assertEqual(download_covers.cover_path(42, folder), folder / "42.jpg")
        # relative, no leading slash: works from catalog.html and book.html
        self.assertEqual(download_covers.cover_url_for(42), "covers/42.jpg")

    def test_small_or_missing_files_are_downloaded_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.assertFalse(download_covers.has_good_file(folder / "1.jpg"))   # missing
            (folder / "2.jpg").write_bytes(b"x" * 100)                          # too small
            self.assertFalse(download_covers.has_good_file(folder / "2.jpg"))
            (folder / "3.jpg").write_bytes(b"x" * 5000)                         # good
            self.assertTrue(download_covers.has_good_file(folder / "3.jpg"))
