# Imports real books from the Open Library API (https://openlibrary.org).
# Usage (from back/):  python manage.py import_books
# Safe to run twice: books whose title already exists are skipped.
import json
import time
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from catalog.models import Author, Book, BookAuthor, Category, Publisher

OPEN_LIBRARY = "https://openlibrary.org"
USER_AGENT = "BookCatalogStudentProject/1.0"
SEARCH_FIELDS = "key,title,author_name,first_publish_year,edition_count,subject,isbn,publisher,cover_i"
NO_DESCRIPTION = "No description available."

# Our genre name -> Open Library search query
GENRE_QUERIES = {
    "Fiction": "subject:fiction",
    "Non-Fiction": "subject:nonfiction",
    "Fantasy": "subject:fantasy",
    "Sci-Fi": "subject:science_fiction",
    "Mystery": "subject:mystery",
    "Biography": "subject:biography",
}
# Used when a query above returns no books
OTHER_SPELLING = {"subject:nonfiction": "subject:non-fiction"}

BOOKS_PER_GENRE = 12
MAX_AUTHORS = 3


# ---------- small functions without network (tested in tests.py) ----------

def work_id(key):
    # "/works/OL138052W" -> "OL138052W"
    return key.rsplit("/", 1)[-1]


def cover_url(cover_i):
    return f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"


def shorten(text, limit=600):
    # Cut long text at the last sentence end before the limit
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))
    if end > 0:
        return cut[:end + 1]
    return cut.rstrip() + "..."


def get_description(work):
    # "description" is either a string or {"type": ..., "value": "..."}
    description = work.get("description") if work else None
    if isinstance(description, dict):
        description = description.get("value")
    if not description:
        return NO_DESCRIPTION
    return shorten(description.strip())


def pick_books(docs, seen_keys, existing_titles, count=BOOKS_PER_GENRE):
    # Keeps the first `count` complete books that we do not have yet.
    # Returns (picked books, number of skipped books).
    picked = []
    skipped = 0
    for doc in docs:
        if len(picked) == count:
            break
        if not (doc.get("cover_i") and doc.get("first_publish_year") and doc.get("author_name")):
            skipped += 1
            continue
        if doc["key"] in seen_keys or doc["title"].lower() in existing_titles:
            skipped += 1
            continue
        # Remember it, so the same book is not picked again in another genre
        seen_keys.add(doc["key"])
        existing_titles.add(doc["title"].lower())
        picked.append(doc)
    return picked, skipped


def bestseller_keys(docs):
    # The 2 books with the most editions become bestsellers
    ranked = sorted(docs, key=lambda doc: doc.get("edition_count", 0), reverse=True)
    return {doc["key"] for doc in ranked[:2]}


def author_names(doc):
    # Remove repeated names (keeps the order), at most MAX_AUTHORS
    return list(dict.fromkeys(doc["author_name"]))[:MAX_AUTHORS]


# ---------- network ----------

def fetch_json(url):
    # One polite request: our User-Agent, 10 s timeout, 1 s pause afterwards.
    # Returns the parsed JSON, or None if anything goes wrong.
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response)
    except Exception as err:
        print(f"    request failed: {err}")
        return None
    finally:
        time.sleep(1)


def search(params):
    return fetch_json(f"{OPEN_LIBRARY}/search.json?{urllib.parse.urlencode(params)}")


def fetch_work(key):
    return fetch_json(f"{OPEN_LIBRARY}/works/{work_id(key)}.json")


# ---------- the command ----------

class Command(BaseCommand):
    help = "Import real books and covers from Open Library"

    def handle(self, *args, **options):
        self.added = 0
        self.skipped = 0
        self.failed = 0
        self.covers = 0

        # Lowercase titles we already have, so we never add a book twice
        existing_titles = {title.lower() for title in Book.objects.values_list("title", flat=True)}
        seen_keys = set()

        for genre, query in GENRE_QUERIES.items():
            self.import_genre(genre, query, seen_keys, existing_titles)

        self.fill_missing_covers()

        self.stdout.write(
            f"\nDone. Added: {self.added}, skipped: {self.skipped}, "
            f"failed: {self.failed}, covers filled: {self.covers}"
        )

    def import_genre(self, genre, query, seen_keys, existing_titles):
        self.stdout.write(f"\n{genre} ({query})")
        params = {"q": query, "limit": 25, "sort": "editions",
                  "language": "eng", "fields": SEARCH_FIELDS}
        data = search(params)

        if data is not None and not data["docs"] and query in OTHER_SPELLING:
            params["q"] = OTHER_SPELLING[query]
            self.stdout.write(f"  nothing found, trying {params['q']}")
            data = search(params)

        if data is None:
            self.failed += 1
            return

        docs = data["docs"]
        books, skipped = pick_books(docs, seen_keys, existing_titles)
        self.skipped += skipped
        bestsellers = bestseller_keys(books)
        category = Category.objects.get(name=genre)

        for doc in books:
            description = get_description(fetch_work(doc["key"]))
            try:
                self.save_book(doc, category, description, doc["key"] in bestsellers)
            except Exception as err:
                self.failed += 1
                self.stdout.write(f"  ! {doc['title']}: {err}")
                continue
            self.added += 1
            self.stdout.write(f"  + {doc['title']} ({doc['first_publish_year']})")

    # Either the whole book (with publisher, authors and links) is saved, or nothing
    @transaction.atomic
    def save_book(self, doc, category, description, is_bestseller):
        publisher = None
        if doc.get("publisher"):
            publisher, created = Publisher.objects.get_or_create(name=doc["publisher"][0])

        # ISBN must be unique in our table, so only use a free one
        isbn = doc["isbn"][0] if doc.get("isbn") else None
        if isbn and Book.objects.filter(isbn=isbn).exists():
            isbn = None

        book = Book.objects.create(
            title=doc["title"],
            publication_year=doc["first_publish_year"],
            isbn=isbn,
            category=category,
            publisher=publisher,
            description=description,
            cover_url=cover_url(doc["cover_i"]),
            is_bestseller=is_bestseller,
            total_copies=3,
            available_copies=3,
        )
        for name in author_names(doc):
            author, created = Author.objects.get_or_create(full_name=name)
            BookAuthor.objects.create(book=book, author=author)

    def fill_missing_covers(self):
        self.stdout.write("\nCovers for books without one")
        books = Book.objects.filter(Q(cover_url__isnull=True) | Q(cover_url=""))

        for book in books.prefetch_related("bookauthor_set__author"):
            params = {"title": book.title, "limit": 1, "fields": "key,cover_i"}
            links = book.bookauthor_set.all()
            if links:
                params["author"] = links[0].author.full_name

            data = search(params)
            if not data or not data["docs"] or not data["docs"][0].get("cover_i"):
                self.stdout.write(f"  - {book.title}: no cover found")
                continue

            doc = data["docs"][0]
            book.cover_url = cover_url(doc["cover_i"])
            if not book.description:
                book.description = get_description(fetch_work(doc["key"]))
            book.save(update_fields=["cover_url", "description"])
            self.covers += 1
            self.stdout.write(f"  * {book.title}: cover added")
