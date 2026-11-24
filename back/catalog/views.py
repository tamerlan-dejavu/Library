# JSON API for the frontend. Every view returns a JsonResponse.
import json
from datetime import timedelta
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Book, BookAuthor, Librarian, Loan, Member, Reservation, Review

BOOKS_PER_PAGE = 12


# ---------- small helpers ----------

def error(message, status=400):
    return JsonResponse({"error": message}, status=status)


def allow(method):
    # Decorator: answer 405 (as JSON) when the HTTP method is wrong
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.method != method:
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
    # createsuperuser has none yet, so we create it on first use)
    member, created = Member.objects.get_or_create(
        user=user, defaults={"full_name": user.username}
    )
    return member


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
    }


def review_author(review):
    # Members from seed.sql have no login, so fall back to their full name
    member = review.member
    if member is None:
        return None
    if member.user is not None:
        return member.user.username
    return member.full_name


# ---------- books ----------

@allow("GET")
def book_list(request):
    books = books_with_rating()
    params = request.GET

    # genre can repeat: ?genre=fantasy&genre=sci-fi -> books of either genre
    genres = params.getlist("genre")
    if genres:
        genre_filter = Q()
        for name in genres:
            genre_filter |= Q(category__name__iexact=name)
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
        .select_related("member__user")
        .order_by("-created_at")
    )

    data = book_to_dict(book)
    data["description"] = book.description
    data["reviews"] = [
        {
            "username": review_author(r),
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at,
        }
        for r in reviews
    ]
    return JsonResponse(data)


# ---------- accounts ----------

@allow("POST")
def register(request):
    data = read_json(request)
    if data is None:
        return error("Invalid JSON")

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    confirm_password = str(data.get("confirm_password", ""))

    # Same rules as front/js/register.js
    if len(username) < 2:
        return error("Username must have at least 2 characters.")
    if User.objects.filter(username=username).exists():
        return error("This username is already taken.")
    if password == "":
        return error("Please enter a password.")
    if password != confirm_password:
        return error("Passwords do not match.")
    try:
        birth_year = int(data.get("birth_year"))
    except (TypeError, ValueError):
        return error("Please enter your birth year.")
    if birth_year < 1900:
        return error("Please enter a real birth year.")
    if timezone.localdate().year - birth_year <= 18:
        return error("You must be older than 18.")

    # Both rows are saved together, or neither of them
    with transaction.atomic():
        user = User.objects.create_user(username=username, password=password)
        Member.objects.create(user=user, full_name=username, birth_year=birth_year)

    login(request, user)
    return JsonResponse({"username": user.username}, status=201)


@allow("POST")
def login_view(request):
    data = read_json(request)
    if data is None:
        return error("Invalid JSON")

    # authenticate() returns the User, or None if the password is wrong
    user = authenticate(
        request,
        username=data.get("username", ""),
        password=data.get("password", ""),
    )
    if user is None:
        return error("Wrong username or password.", 401)

    login(request, user)
    return JsonResponse({"username": user.username})


@allow("POST")
def logout_view(request):
    logout(request)
    return JsonResponse({"logged_in": False})


# ensure_csrf_cookie: always send the csrftoken cookie, so the frontend
# can put it into the X-CSRFToken header of its POST requests
@ensure_csrf_cookie
@allow("GET")
def me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"logged_in": False})

    member = get_member(request.user)
    loans = Loan.objects.filter(member=member).select_related("book").order_by("-loan_date")
    reviews = Review.objects.filter(member=member).select_related("book").order_by("-created_at")

    return JsonResponse({
        "logged_in": True,
        "username": request.user.username,
        "loans": [
            {
                "title": loan.book.title,
                "loan_date": loan.loan_date,
                "due_date": loan.due_date,
                "return_date": loan.return_date,
            }
            for loan in loans
        ],
        "reviews": [
            {"book_title": r.book.title, "rating": r.rating, "comment": r.comment}
            for r in reviews
        ],
    })


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
