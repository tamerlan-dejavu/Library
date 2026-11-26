# JSON API for the frontend. Every view returns a JsonResponse.
import json
import re
from datetime import timedelta
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, Max, Min, Q
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


# ---------- small helpers ----------

def error(message, status=400, field=None):
    # field (optional) tells the form which input the message belongs to
    data = {"error": message}
    if field:
        data["field"] = field
    return JsonResponse(data, status=status)


def allow(*methods):
    # Decorator: answer 405 (as JSON) when the HTTP method is wrong,
    # e.g. @allow("GET") or @allow("GET", "PATCH")
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return error("Method not allowed", 405)
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def login_required_json(view):
    # Like Django's login_required, but answers 401 JSON instead of a redirect
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return error("Login required", 401)
        return view(request, *args, **kwargs)
    return wrapper


def read_json(request):
    # Returns the JSON body as a dict, or None if it is not valid JSON
    try:
        data = json.loads(request.body)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def get_member(user):
    # Every logged-in user needs a Member row (e.g. an admin created by
    # createsuperuser has none yet, so we create it on first use from
    # the account data; names and e-mail may not be empty in the table)
    member, created = Member.objects.get_or_create(
        user=user,
        defaults={
            "first_name": user.first_name or user.username,
            "last_name": user.last_name or user.username,
            "email": (user.email or f"{user.username}@users.local").lower(),
        },
    )
    return member


def is_valid_name(name):
    # At least 2 characters: letters of any alphabet (Kazakh, Russian,
    # English, ...), and also space, hyphen and apostrophe
    return (2 <= len(name) <= 150
            and any(ch.isalpha() for ch in name)
            and all(ch.isalpha() or ch in " -'’" for ch in name))


def email_is_taken(email):
    # Compare without letter case, with members and with login accounts
    return (Member.objects.filter(email__iexact=email).exists()
            or User.objects.filter(Q(username__iexact=email) | Q(email__iexact=email)).exists())


def books_with_rating():
    # Base query: book + category in one JOIN, authors in one extra query,
    # and the average review rating calculated by the database
    return (
        Book.objects.select_related("category")
        .prefetch_related("bookauthor_set__author")
        .annotate(avg_rating=Avg("review__rating"))
    )


def book_to_dict(book):
    rating = None
    if book.avg_rating is not None:
        rating = round(book.avg_rating, 1)
    return {
        "id": book.book_id,
        "title": book.title,
        "authors": [link.author.full_name for link in book.bookauthor_set.all()],
        "genre": book.category.name if book.category else None,
        "year": book.publication_year,
        "cover_url": book.cover_url,
        "rating": rating,
        "is_bestseller": book.is_bestseller,
        "available_copies": book.available_copies,
        "total_copies": book.total_copies,
    }


def first_author(book):
    # Name of the first author of a book (or "" if it has none)
    link = book.bookauthor_set.first()
    return link.author.full_name if link else ""


def review_author(review):
    # Short public name: first name + first letter of the last name,
    # e.g. "Алихан Б." (the full name is not shown to other visitors)
    member = review.member
    if member is None:
        return None
    return f"{member.first_name} {member.last_name[:1]}."


# ---------- books ----------

@allow("GET")
def book_list(request):
    books = books_with_rating()
    params = request.GET

    # genre can repeat: ?genre=1&genre=3 -> books of either genre.
    # A number is a category id, any other text a category name.
    genres = params.getlist("genre")
    if genres:
        genre_filter = Q()
        for value in genres:
            if value.isdigit():
                genre_filter |= Q(category_id=int(value))
            else:
                genre_filter |= Q(category__name__iexact=value)
        books = books.filter(genre_filter)

    # Numbers come as text, so convert them and report bad input
    try:
        if params.get("year_from"):
            books = books.filter(publication_year__gte=int(params["year_from"]))
        if params.get("year_to"):
            books = books.filter(publication_year__lte=int(params["year_to"]))
        if params.get("rating"):
            books = books.filter(avg_rating__gte=float(params["rating"]))
    except ValueError:
        return error("year_from, year_to and rating must be numbers")

    # Search in the title OR in the name of any author of the book
    q = params.get("q", "").strip()
    if q:
        by_author = BookAuthor.objects.filter(author__full_name__icontains=q)
        books = books.filter(
            Q(title__icontains=q) | Q(book_id__in=by_author.values("book_id"))
        )

    if params.get("bestseller") == "1":
        books = books.filter(is_bestseller=True)

    # get_page() also handles a missing or wrong page number
    paginator = Paginator(books.order_by("title"), BOOKS_PER_PAGE)
    page = paginator.get_page(params.get("page"))

    return JsonResponse({
        "books": [book_to_dict(book) for book in page],
        "page": page.number,
        "pages": paginator.num_pages,
    })


@allow("GET")
def book_detail(request, book_id):
    book = books_with_rating().filter(book_id=book_id).first()
    if book is None:
        return error("Book not found", 404)

    reviews = (
        Review.objects.filter(book=book)
        .select_related("member")
        .order_by("-created_at")
    )

    data = book_to_dict(book)
    data["description"] = book.description
    data["reviews"] = [
        {
            "author": review_author(r),
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at,
        }
        for r in reviews
    ]
    return JsonResponse(data)


@allow("GET")
def filters(request):
    # Data for the catalog filters and the Home categories:
    # every genre with its number of books, and the range of years
    genres = Category.objects.annotate(count=Count("book")).order_by("name")
    years = Book.objects.aggregate(year_min=Min("publication_year"), year_max=Max("publication_year"))
    return JsonResponse({
        "genres": [{"id": g.category_id, "name": g.name, "count": g.count} for g in genres],
        "year_min": years["year_min"],
        "year_max": years["year_max"],
    })


# ---------- accounts ----------

@allow("POST")
def register(request):
    data = read_json(request)
    if data is None:
        return error("Invalid JSON")

    first_name = str(data.get("first_name", "")).strip()
    last_name = str(data.get("last_name", "")).strip()
    # E-mail addresses are stored in lower case
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    password2 = str(data.get("password2", ""))

    # Same rules as front/js/register.js; "field" names the form input
    if not is_valid_name(first_name):
        return error("First name: at least 2 letters (spaces, - and ' are allowed).", field="first_name")
    if not is_valid_name(last_name):
        return error("Last name: at least 2 letters (spaces, - and ' are allowed).", field="last_name")
    try:
        validate_email(email)
    except ValidationError:
        return error("Please enter a valid e-mail address.", field="email")
    if len(email) > 150:  # Django keeps the e-mail as the login name (max 150)
        return error("This e-mail address is too long.", field="email")
    if email_is_taken(email):
        return error("An account with this e-mail already exists.", field="email")
    if password == "":
        return error("Please enter a password.", field="password")
    if password != password2:
        return error("Passwords do not match.", field="password2")
    try:
        birth_year = int(data.get("birth_year"))
    except (TypeError, ValueError):
        return error("Please enter your birth year.", field="birth_year")
    if birth_year < 1900:
        return error("Please enter a real birth year.", field="birth_year")
    if timezone.localdate().year - birth_year <= 18:
        return error("You must be older than 18.", field="birth_year")

    # Both rows are saved together, or neither of them.
    # The e-mail is also the (hidden) Django username, so login works by e-mail.
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=email, email=email, password=password,
                first_name=first_name, last_name=last_name,
            )
            Member.objects.create(user=user, first_name=first_name, last_name=last_name,
                                  email=email, birth_year=birth_year)
    except IntegrityError:
        # Someone registered the same e-mail at the same moment
        return error("An account with this e-mail already exists.", field="email")

    login(request, user)
    return JsonResponse({"first_name": first_name}, status=201)


@allow("POST")
def login_view(request):
    data = read_json(request)
    if data is None:
        return error("Invalid JSON")

    # The Django username of a member is the e-mail in lower case.
    # authenticate() returns the User, or None if e-mail or password is wrong.
    user = authenticate(
        request,
        username=str(data.get("email", "")).strip().lower(),
        password=str(data.get("password", "")),
    )
    if user is None:
        # One message for both cases, so nobody can test which e-mails exist
        return error("Invalid email or password.", 401)

    login(request, user)
    return JsonResponse({"first_name": get_member(user).first_name})


@allow("POST")
def logout_view(request):
    logout(request)
    return JsonResponse({"logged_in": False})


# ensure_csrf_cookie: always send the csrftoken cookie, so the frontend
# can put it into the X-CSRFToken header of its POST requests
@ensure_csrf_cookie
@allow("GET", "PATCH")
def me(request):
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
    with_authors = ("book__bookauthor_set__author",)
    loans = Loan.objects.filter(member=member).select_related("book") \
        .prefetch_related(*with_authors).order_by("-loan_date")
    reservations = Reservation.objects.filter(member=member, status="pending") \
        .select_related("book").prefetch_related(*with_authors).order_by("-reserved_at")
    reviews = Review.objects.filter(member=member).select_related("book") \
        .prefetch_related(*with_authors).order_by("-created_at")
    # The member's own rating of each book, shown next to the loan
    my_ratings = {r.book_id: r.rating for r in reviews}

    return {
        "logged_in": True,
        "first_name": member.first_name,
        "last_name": member.last_name,
        "email": member.email,
        "birth_year": member.birth_year,
        "phones": [p.phone for p in member.memberphone_set.order_by("member_phone_id")],
        "loans": [
            {
                "book_id": loan.book_id,
                "title": loan.book.title,
                "author": first_author(loan.book),
                "loan_date": loan.loan_date,
                "due_date": loan.due_date,
                "return_date": loan.return_date,
                "rating": my_ratings.get(loan.book_id),
            }
            for loan in loans
        ],
        "reservations": [
            {
                "book_id": res.book_id,
                "title": res.book.title,
                "author": first_author(res.book),
                "reserved_at": res.reserved_at,
                "rating": my_ratings.get(res.book_id),
            }
            for res in reservations
        ],
        "reviews": [
            {
                "book_id": r.book_id,
                "book_title": r.book.title,
                "author": first_author(r.book),
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at,
            }
            for r in reviews
        ],
    }


def update_profile(request, member):
    # PATCH /api/me/ with {"first_name", "last_name", "phones": [...]}.
    # E-mail and birth year cannot be changed here.
    data = read_json(request)
    if data is None:
        return error("Invalid JSON")

    first_name = str(data.get("first_name", "")).strip()
    last_name = str(data.get("last_name", "")).strip()
    phones = data.get("phones", [])

    if not is_valid_name(first_name):
        return error("First name: at least 2 letters (spaces, - and ' are allowed).", field="first_name")
    if not is_valid_name(last_name):
        return error("Last name: at least 2 letters (spaces, - and ' are allowed).", field="last_name")
    if not isinstance(phones, list):
        return error("Phones must be a list.", field="phones")
    # Empty rows from the form are ignored; spaces inside a number too
    phones = [str(p).replace(" ", "").strip() for p in phones if str(p).strip()]
    if len(phones) > MAX_PHONES:
        return error(f"At most {MAX_PHONES} phone numbers.", field="phones")
    for phone in phones:
        if not PHONE_PATTERN.match(phone):
            return error(f"{phone}: use + and 10-15 digits, e.g. +77011234567.", field="phones")
    if len(set(phones)) != len(phones):
        return error("The same phone number is entered twice.", field="phones")

    # Names in both tables and the whole set of phones change together
    with transaction.atomic():
        member.first_name = first_name
        member.last_name = last_name
        member.save(update_fields=["first_name", "last_name"])
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=["first_name", "last_name"])
        MemberPhone.objects.filter(member=member).delete()
        MemberPhone.objects.bulk_create([MemberPhone(member=member, phone=p) for p in phones])

    return JsonResponse(profile_data(member))


# ---------- actions on a book ----------

@allow("POST")
@login_required_json
def add_review(request, book_id):
    book = Book.objects.filter(book_id=book_id).first()
    if book is None:
        return error("Book not found", 404)

    data = read_json(request)
    if data is None:
        return error("Invalid JSON")

    try:
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        return error("Rating must be a number from 1 to 5.")
    if rating < 1 or rating > 5:
        return error("Rating must be a number from 1 to 5.")

    member = get_member(request.user)
    # The database also has UNIQUE (book_id, member_id); we check first
    # so the user gets a clear message instead of a database error
    if Review.objects.filter(book=book, member=member).exists():
        return error("You have already reviewed this book.")

    review = Review.objects.create(
        book=book, member=member, rating=rating,
        comment=str(data.get("comment", "")).strip(),
    )
    return JsonResponse({"id": review.review_id, "rating": rating}, status=201)


@allow("POST")
@login_required_json
def borrow(request, book_id):
    member = get_member(request.user)

    with transaction.atomic():
        # select_for_update() locks the book row until the transaction ends,
        # so two people cannot take the last copy at the same time
        book = Book.objects.select_for_update().filter(book_id=book_id).first()
        if book is None:
            return error("Book not found", 404)

        # One active loan and one pending reservation per member per book
        if Loan.objects.filter(book=book, member=member, return_date__isnull=True).exists():
            return error("You already have this book.")
        if Reservation.objects.filter(book=book, member=member, status="pending").exists():
            return error("You already reserved this book.")

        if book.available_copies > 0:
            today = timezone.localdate()
            Loan.objects.create(
                book=book,
                member=member,
                librarian=Librarian.objects.get(full_name="Online"),
                loan_date=today,
                due_date=today + timedelta(days=14),
            )
            book.available_copies -= 1
            book.save(update_fields=["available_copies"])
            return JsonResponse({
                "result": "borrowed",
                "message": f"You borrowed \"{book.title}\". Return it by {today + timedelta(days=14)}.",
            })

        Reservation.objects.create(book=book, member=member, status="pending")
        return JsonResponse({
            "result": "reserved",
            "message": f"No free copies of \"{book.title}\". You are on the waiting list.",
        })
