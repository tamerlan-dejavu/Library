# JSON API for the frontend. Every view does the same steps:
# read the request -> check it -> save -> return JSON.
import json
import re
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Avg, BooleanField, Count, ExpressionWrapper, Max, Min, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import (
    Book, BookAuthor, Category, Librarian, Loan, Member, MemberPhone, Reservation, Review,
)

# Same rule as the CHECK of member_phone.phone in schema.sql
PHONE_PATTERN = re.compile(r"^\+?[0-9]{10,15}$")
MAX_PHONES = 5
BOOKS_PER_PAGE = 12
NAME_RULE = "at least 2 letters (spaces, - and ' are allowed)."


# ---------- small helpers ----------

def error(message, status=400, field=None):
    # field (optional) tells the form which input the message belongs to
    data = {"error": message}
    if field:
        data["field"] = field
    return JsonResponse(data, status=status)


def read_json(request):
    # Returns the JSON body as a dict, or None if it is not valid JSON
    try:
        data = json.loads(request.body)
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def get_member(user):
    # Every logged-in user needs a Member row (an admin made with
    # createsuperuser has none yet, so we create it on first use)
    member, created = Member.objects.get_or_create(
        user=user,
        defaults={
            "first_name": user.first_name or user.username,
            "last_name": user.last_name or user.username,
            "email": (user.email or user.username + "@users.local").lower(),
        },
    )
    return member


def is_valid_name(name):
    # 2-150 characters: letters of any alphabet, space, hyphen, apostrophe
    if len(name) < 2 or len(name) > 150:
        return False
    has_letter = False
    for ch in name:
        if ch.isalpha():
            has_letter = True
        elif ch not in " -'’":
            return False
    return has_letter


def check_names(first_name, last_name):
    # Returns an error response for a bad name, or None when both are fine
    if not is_valid_name(first_name):
        return error("First name: " + NAME_RULE, field="first_name")
    if not is_valid_name(last_name):
        return error("Last name: " + NAME_RULE, field="last_name")
    return None


def clean_phones(phones):
    # Returns (list of phones, None) or (None, error response).
    # Empty rows from the form are ignored; spaces inside a number too.
    if not isinstance(phones, list):
        return None, error("Phones must be a list.", field="phones")
    result = []
    for phone in phones:
        phone = str(phone).replace(" ", "").strip()
        if phone == "":
            continue
        if not PHONE_PATTERN.match(phone):
            return None, error(phone + ": use + and 10-15 digits, e.g. +77011234567.", field="phones")
        if phone in result:
            return None, error("The same phone number is entered twice.", field="phones")
        result.append(phone)
    if len(result) > MAX_PHONES:
        return None, error("At most " + str(MAX_PHONES) + " phone numbers.", field="phones")
    return result, None


def email_is_taken(email):
    # Compare without letter case, with members and with login accounts
    if Member.objects.filter(email__iexact=email).exists():
        return True
    return User.objects.filter(Q(username__iexact=email) | Q(email__iexact=email)).exists()


# ---------- books ----------

def books_with_rating():
    # Book + category in one JOIN, authors in one extra query,
    # and the average review rating calculated by the database
    books = Book.objects.select_related("category").prefetch_related("bookauthor_set__author")
    return books.annotate(avg_rating=Avg("review__rating"))


def book_to_dict(book):
    authors = []
    for link in book.bookauthor_set.all():
        authors.append(link.author.full_name)
    rating = None
    if book.avg_rating is not None:
        rating = round(book.avg_rating, 1)
    genre = None
    if book.category:
        genre = book.category.name
    return {
        "id": book.book_id, "title": book.title, "authors": authors, "genre": genre,
        "year": book.publication_year, "cover_url": book.cover_url, "rating": rating,
        "is_bestseller": book.is_bestseller, "available_copies": book.available_copies,
        "total_copies": book.total_copies,
    }


def first_author(book):
    # Name of the first author of a book (or "" if it has none)
    link = book.bookauthor_set.first()
    if link is None:
        return ""
    return link.author.full_name


def filter_books(books, params):
    # Applies genre, year, rating, search and bestseller filters.
    # Returns the books, or None when a number in the URL is wrong.
    genre_filter = Q()
    for value in params.getlist("genre"):   # ?genre=1&genre=3 (id or name)
        if value.isdigit():
            genre_filter |= Q(category_id=int(value))
        else:
            genre_filter |= Q(category__name__iexact=value)
    books = books.filter(genre_filter)
    try:
        if params.get("year_from"):
            books = books.filter(publication_year__gte=int(params["year_from"]))
        if params.get("year_to"):
            books = books.filter(publication_year__lte=int(params["year_to"]))
        if params.get("rating"):
            books = books.filter(avg_rating__gte=float(params["rating"]))
    except ValueError:
        return None
    q = params.get("q", "").strip()
    if q:   # the title OR the name of any author
        by_author = BookAuthor.objects.filter(author__full_name__icontains=q)
        books = books.filter(Q(title__icontains=q) | Q(book_id__in=by_author.values("book_id")))
    return books


def book_list(request):
    if request.method != "GET":
        return error("Method not allowed", 405)
    books = filter_books(books_with_rating(), request.GET)
    if books is None:
        return error("year_from, year_to and rating must be numbers")

    if request.GET.get("bestseller") == "1":
        # Bestsellers with a cover first, then by id
        # (SQL: ORDER BY (cover_url IS NULL), book_id)
        no_cover = ExpressionWrapper(Q(cover_url__isnull=True), output_field=BooleanField())
        books = books.filter(is_bestseller=True).annotate(no_cover=no_cover).order_by("no_cover", "book_id")
    else:
        books = books.order_by("title")

    # get_page() also handles a missing or wrong page number
    paginator = Paginator(books, BOOKS_PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))
    result = []
    for book in page:
        result.append(book_to_dict(book))
    return JsonResponse({"books": result, "page": page.number, "pages": paginator.num_pages})


def book_detail(request, book_id):
    if request.method != "GET":
        return error("Method not allowed", 405)
    book = books_with_rating().filter(book_id=book_id).first()
    if book is None:
        return error("Book not found", 404)

    data = book_to_dict(book)
    data["description"] = book.description
    data["reviews"] = []
    for r in Review.objects.filter(book=book).select_related("member").order_by("-created_at"):
        # Public name: first name + first letter of the last name ("Алихан Б.")
        author = None
        if r.member is not None:
            author = r.member.first_name + " " + r.member.last_name[:1] + "."
        data["reviews"].append({"author": author, "rating": r.rating,
                                "comment": r.comment, "created_at": r.created_at})
    return JsonResponse(data)


def filters(request):
    # Every genre with its number of books, and the range of years
    if request.method != "GET":
        return error("Method not allowed", 405)
    genres = []
    for g in Category.objects.annotate(count=Count("book")).order_by("name"):
        genres.append({"id": g.category_id, "name": g.name, "count": g.count})
    years = Book.objects.aggregate(year_min=Min("publication_year"), year_max=Max("publication_year"))
    return JsonResponse({"genres": genres, "year_min": years["year_min"], "year_max": years["year_max"]})


# ---------- accounts ----------

def check_registration(data):
    # Same rules as front/js/register.js. Returns an error response or None.
    email = data["email"]
    bad_name = check_names(data["first_name"], data["last_name"])
    if bad_name:
        return bad_name
    try:
        validate_email(email)
    except ValidationError:
        return error("Please enter a valid e-mail address.", field="email")
    if len(email) > 150:   # the e-mail is also the login name (max 150)
        return error("This e-mail address is too long.", field="email")
    if email_is_taken(email):
        return error("An account with this e-mail already exists.", field="email")
    if data["password"] == "":
        return error("Please enter a password.", field="password")
    if data["password"] != data["password2"]:
        return error("Passwords do not match.", field="password2")
    return None


def check_birth_year(value):
    # Returns (year, None) or (None, error response)
    try:
        year = int(value)
    except (TypeError, ValueError):
        return None, error("Please enter your birth year.", field="birth_year")
    if year < 1900:
        return None, error("Please enter a real birth year.", field="birth_year")
    if timezone.localdate().year - year <= 18:
        return None, error("You must be older than 18.", field="birth_year")
    return year, None


def register(request):
    if request.method != "POST":
        return error("Method not allowed", 405)
    body = read_json(request)
    if body is None:
        return error("Invalid JSON")
    data = {
        "first_name": str(body.get("first_name", "")).strip(),
        "last_name": str(body.get("last_name", "")).strip(),
        "email": str(body.get("email", "")).strip().lower(),   # stored in lower case
        "password": str(body.get("password", "")),
        "password2": str(body.get("password2", "")),
    }
    problem = check_registration(data)
    if problem:
        return problem
    birth_year, problem = check_birth_year(body.get("birth_year"))
    if problem:
        return problem

    # Both rows are saved together, or neither of them. The e-mail is
    # also the (hidden) Django username, so login works by e-mail.
    try:
        with transaction.atomic():
            user = User.objects.create_user(username=data["email"], email=data["email"],
                                            password=data["password"],
                                            first_name=data["first_name"], last_name=data["last_name"])
            Member.objects.create(user=user, first_name=data["first_name"], last_name=data["last_name"],
                                  email=data["email"], birth_year=birth_year)
    except IntegrityError:   # the same e-mail registered at the same moment
        return error("An account with this e-mail already exists.", field="email")

    login(request, user)
    return JsonResponse({"first_name": data["first_name"]}, status=201)


def login_view(request):
    if request.method != "POST":
        return error("Method not allowed", 405)
    data = read_json(request)
    if data is None:
        return error("Invalid JSON")

    # The Django username of a member is the e-mail in lower case
    email = str(data.get("email", "")).strip().lower()
    user = authenticate(request, username=email, password=str(data.get("password", "")))
    if user is None:
        # One message for both cases, so nobody can test which e-mails exist
        return error("Invalid email or password.", 401)

    login(request, user)
    return JsonResponse({"first_name": get_member(user).first_name})


def logout_view(request):
    if request.method != "POST":
        return error("Method not allowed", 405)
    logout(request)
    return JsonResponse({"logged_in": False})


# ensure_csrf_cookie: always send the csrftoken cookie, so the frontend
# can put it into the X-CSRFToken header of its POST and PATCH requests
@ensure_csrf_cookie
def me(request):
    if request.method not in ("GET", "PATCH"):
        return error("Method not allowed", 405)
    if not request.user.is_authenticated:
        if request.method == "PATCH":
            return error("Login required", 401)
        return JsonResponse({"logged_in": False})

    member = get_member(request.user)
    if request.method == "PATCH":
        return update_profile(request, member)
    return JsonResponse(profile_data(member))


def profile_data(member):
    # Everything the profile page shows about the logged-in member
    authors = "book__bookauthor_set__author"
    reviews = Review.objects.filter(member=member).select_related("book") \
        .prefetch_related(authors).order_by("-created_at")
    my_ratings = {}   # book_id -> the member's own rating, shown next to the loan
    review_list = []
    for r in reviews:
        my_ratings[r.book_id] = r.rating
        review_list.append({"book_id": r.book_id, "book_title": r.book.title, "author": first_author(r.book),
                            "rating": r.rating, "comment": r.comment, "created_at": r.created_at})

    loans = []
    for loan in Loan.objects.filter(member=member).select_related("book") \
            .prefetch_related(authors).order_by("-loan_date"):
        loans.append({"book_id": loan.book_id, "title": loan.book.title, "author": first_author(loan.book),
                      "loan_date": loan.loan_date, "due_date": loan.due_date,
                      "return_date": loan.return_date, "rating": my_ratings.get(loan.book_id)})

    reservations = []
    for res in Reservation.objects.filter(member=member, status="pending").select_related("book") \
            .prefetch_related(authors).order_by("-reserved_at"):
        reservations.append({"book_id": res.book_id, "title": res.book.title, "author": first_author(res.book),
                             "reserved_at": res.reserved_at, "rating": my_ratings.get(res.book_id)})

    phones = []
    for p in member.memberphone_set.order_by("member_phone_id"):
        phones.append(p.phone)
    return {"logged_in": True, "first_name": member.first_name, "last_name": member.last_name,
            "email": member.email, "birth_year": member.birth_year, "phones": phones,
            "loans": loans, "reservations": reservations, "reviews": review_list}


def update_profile(request, member):
    # PATCH /api/me/ with {"first_name", "last_name", "phones": [...]}.
    # E-mail and birth year cannot be changed here.
    data = read_json(request)
    if data is None:
        return error("Invalid JSON")
    first_name = str(data.get("first_name", "")).strip()
    last_name = str(data.get("last_name", "")).strip()
    problem = check_names(first_name, last_name)
    if problem:
        return problem
    phones, problem = clean_phones(data.get("phones", []))
    if problem:
        return problem

    # Names in both tables and the whole set of phones change together
    with transaction.atomic():
        member.first_name = first_name
        member.last_name = last_name
        member.save(update_fields=["first_name", "last_name"])
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save(update_fields=["first_name", "last_name"])
        MemberPhone.objects.filter(member=member).delete()
        for phone in phones:
            MemberPhone.objects.create(member=member, phone=phone)
    return JsonResponse(profile_data(member))


# ---------- actions on a book ----------

def add_review(request, book_id):
    if request.method != "POST":
        return error("Method not allowed", 405)
    if not request.user.is_authenticated:
        return error("Login required", 401)
    book = Book.objects.filter(book_id=book_id).first()
    if book is None:
        return error("Book not found", 404)
    data = read_json(request)
    if data is None:
        return error("Invalid JSON")

    try:
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        rating = 0
    if rating < 1 or rating > 5:
        return error("Rating must be a number from 1 to 5.")

    member = get_member(request.user)
    # The database also has UNIQUE (book_id, member_id); we check first
    # so the user gets a clear message instead of a database error
    if Review.objects.filter(book=book, member=member).exists():
        return error("You have already reviewed this book.")

    review = Review.objects.create(book=book, member=member, rating=rating,
                                   comment=str(data.get("comment", "")).strip())
    return JsonResponse({"id": review.review_id, "rating": rating}, status=201)


# check the member has no open loan and no waiting reservation of this book
def borrow_problem(book, member):
    if Loan.objects.filter(book=book, member=member, return_date__isnull=True).exists():
        return error("You already have this book.")
    if Reservation.objects.filter(book=book, member=member, status="pending").exists():
        return error("You already reserved this book.")
    return None


# create the loan (14 days, librarian "Online") and decrease the free copies
def create_loan(book, member):
    today = timezone.localdate()
    due_date = today + timedelta(days=14)
    Loan.objects.create(book=book, member=member, librarian=Librarian.objects.get(full_name="Online"),
                        loan_date=today, due_date=due_date)
    book.available_copies -= 1
    book.save(update_fields=["available_copies"])
    return JsonResponse({"result": "borrowed",
                         "message": f"You borrowed \"{book.title}\". Return it by {due_date}."})


# no free copy: put the member on the waiting list
def create_reservation(book, member):
    Reservation.objects.create(book=book, member=member, status="pending")
    return JsonResponse({"result": "reserved",
                         "message": f"No free copies of \"{book.title}\". You are on the waiting list."})


def borrow(request, book_id):
    if request.method != "POST":
        return error("Method not allowed", 405)
    if not request.user.is_authenticated:
        return error("Login required", 401)
    member = get_member(request.user)

    with transaction.atomic():
        # select_for_update() locks the book row until the transaction ends,
        # so two people cannot take the last copy at the same time
        book = Book.objects.select_for_update().filter(book_id=book_id).first()
        if book is None:
            return error("Book not found", 404)
        problem = borrow_problem(book, member)
        if problem:
            return problem
        if book.available_copies > 0:
            return create_loan(book, member)
        return create_reservation(book, member)
