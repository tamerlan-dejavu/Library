# Copies book covers from Open Library into front/covers/, so the website
# does not depend on Open Library while it runs.
# Usage (from back/):
#   python manage.py download_covers              1) download the files
#   python manage.py download_covers --update-db  2) point cover_url to them
# Safe to run twice: existing files are skipped, unchanged rows are not saved.
import time
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from catalog.models import Book

USER_AGENT = "BookCatalogStudentProject/1.0"
OPEN_LIBRARY_COVERS = "https://covers.openlibrary.org/"
COVERS_DIR = settings.FRONTEND_DIR / "covers"
MIN_SIZE = 1024        # smaller files are treated as broken
TIMEOUT = 60           # the cover server can be very slow
ATTEMPTS = 3
PAUSE = 3              # seconds between attempts for one file


# ---------- small functions without network (tested in tests.py) ----------

def is_open_library_cover(url):
    return bool(url) and url.startswith(OPEN_LIBRARY_COVERS)


def medium_url(url):
    # ".../b/id/123-L.jpg" -> ".../b/id/123-M.jpg"
    return url.replace("-L.jpg", "-M.jpg")


def cover_path(book_id, folder=COVERS_DIR):
    # Where the file is stored: front/covers/<book_id>.jpg
    return folder / f"{book_id}.jpg"


def cover_url_for(book_id):
    # What we save in the database. Relative, without "/", so it works
    # from catalog.html and book.html (both are in front/)
    return f"covers/{book_id}.jpg"


def has_good_file(path):
    return path.exists() and path.stat().st_size > MIN_SIZE


# ---------- network ----------

def download(url, path):
    # Up to ATTEMPTS tries. Returns None on success or the last error text.
    error = "unknown error"
    for attempt in range(1, ATTEMPTS + 1):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            # urlopen follows the redirect to archive.org by itself
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                content_type = response.headers.get("Content-Type", "")
                data = response.read()
            if not content_type.startswith("image/"):
                error = f"not an image ({content_type})"
            elif len(data) <= MIN_SIZE:
                error = f"too small ({len(data)} bytes)"
            else:
                # Write to a temporary name first, so a half-written file
                # never looks like a finished cover
                tmp = path.with_suffix(".part")
                tmp.write_bytes(data)
                tmp.replace(path)
                return None
        except Exception as err:
            error = str(err)
        finally:
            time.sleep(1)   # at most 1 request per second overall
        if attempt < ATTEMPTS:
            time.sleep(PAUSE)
    return error


class Command(BaseCommand):
    help = "Download Open Library covers to front/covers/ (and optionally use them)"

    def add_arguments(self, parser):
        parser.add_argument("--update-db", action="store_true",
                            help="set cover_url to covers/<id>.jpg for downloaded files")

    def handle(self, *args, **options):
        if options["update_db"]:
            self.update_db()
        else:
            self.download_all()

    def download_all(self):
        COVERS_DIR.mkdir(parents=True, exist_ok=True)
        downloaded, skipped, failed = 0, 0, []

        for book in Book.objects.order_by("book_id"):
            if not is_open_library_cover(book.cover_url):
                continue
            path = cover_path(book.book_id)
            if has_good_file(path):
                skipped += 1
                continue
            error = download(medium_url(book.cover_url), path)
            if error is None:
                downloaded += 1
                self.stdout.write(f"  + {book.book_id} {book.title}")
            else:
                failed.append(book.book_id)
                self.stdout.write(f"  ! {book.book_id} {book.title}: {error}")

        self.stdout.write(f"\nDownloaded: {downloaded}, skipped (already there): {skipped}, "
                          f"failed: {len(failed)}")
        if failed:
            self.stdout.write("Failed book ids: " + ", ".join(str(i) for i in failed))

    def update_db(self):
        updated = 0
        for book in Book.objects.order_by("book_id"):
            new_url = cover_url_for(book.book_id)
            # Only books that have a downloaded file; the others keep their URL
            if has_good_file(cover_path(book.book_id)) and book.cover_url != new_url:
                book.cover_url = new_url
                book.save(update_fields=["cover_url"])
                updated += 1
        self.stdout.write(f"Updated cover_url of {updated} books")
