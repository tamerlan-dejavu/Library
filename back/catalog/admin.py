# CRUD admin panel for all 11 tables
from django.contrib import admin
from django.utils import timezone

from .models import (
    Author, Book, BookAuthor, Category, Librarian,
    Loan, Member, MemberPhone, Publisher, Reservation, Review,
)

# Titles shown in the browser tab and at the top of every admin page
admin.site.site_header = "Book Catalog administration"
admin.site.site_title = "Book Catalog admin"
admin.site.index_title = "Library data"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_id", "name")
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("publisher_id", "name", "country")
    search_fields = ("name", "country")
    list_filter = ("country",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("author_id", "full_name", "birth_year", "country")
    search_fields = ("full_name",)
    list_filter = ("country",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("book_id", "title", "authors", "publication_year", "category",
                    "publisher", "is_bestseller", "available_copies", "total_copies")
    # "category__name" searches inside the related table
    search_fields = ("title", "isbn", "category__name", "publisher__name",
                     "bookauthor__author__full_name")
    list_filter = ("category", "is_bestseller", "publisher")
    list_per_page = 25

    def get_queryset(self, request):
        # Load the authors of all listed books with one extra query
        return super().get_queryset(request).prefetch_related("bookauthor_set__author")

    @admin.display(description="Authors")
    def authors(self, book):
        return ", ".join(link.author.full_name for link in book.bookauthor_set.all())


@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ("book", "author")
    search_fields = ("book__title", "author__full_name")
    list_filter = ("author",)


# Phones are edited inside the member page (weak entity of member)
class MemberPhoneInline(admin.TabularInline):
    model = MemberPhone
    extra = 1


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("member_id", "first_name", "last_name", "email", "birth_year",
                    "city", "user", "registered_at")
    search_fields = ("first_name", "last_name", "email", "city", "memberphone__phone")
    list_filter = ("city", "birth_year")
    ordering = ("last_name", "first_name")
    inlines = [MemberPhoneInline]
    # Order of the fields in the form
    fields = ("first_name", "last_name", "email", "birth_year", "city", "street",
              "user", "registered_at")
    # Filled by the database (DEFAULT now()), so not editable in the form
    readonly_fields = ("registered_at",)


@admin.register(MemberPhone)
class MemberPhoneAdmin(admin.ModelAdmin):
    list_display = ("member_phone_id", "member", "phone")
    search_fields = ("phone", "member__first_name", "member__last_name")
    list_filter = ("member__city",)


@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ("librarian_id", "full_name", "email")
    search_fields = ("full_name", "email")
    list_filter = ("full_name",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("loan_id", "book", "member", "librarian",
                    "loan_date", "due_date", "return_date", "status")
    search_fields = ("book__title", "member__first_name", "member__last_name")
    list_filter = ("librarian", "loan_date", "due_date", "return_date")
    list_select_related = ("book", "member", "librarian")

    # Derived value, computed for display only (not stored)
    @admin.display(description="Status")
    def status(self, loan):
        if loan.return_date:
            return "Returned"
        if loan.due_date < timezone.localdate():
            return "Overdue"
        return "On loan"


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("reservation_id", "book", "member", "status", "reserved_at")
    search_fields = ("book__title", "member__first_name", "member__last_name")
    list_filter = ("status",)
    readonly_fields = ("reserved_at",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("review_id", "book", "member", "rating", "created_at")
    search_fields = ("book__title", "member__first_name", "member__last_name", "comment")
    list_filter = ("rating",)
    readonly_fields = ("created_at",)
