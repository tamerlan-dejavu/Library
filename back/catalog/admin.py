# CRUD admin panel for all 10 tables
from django.contrib import admin

from .models import (
    Author, Book, BookAuthor, Category, Librarian,
    Loan, Member, MemberPhone, Publisher, Reservation, Review,
)


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
    list_display = ("book_id", "title", "publication_year", "category",
                    "publisher", "is_bestseller", "available_copies", "total_copies")
    # "category__name" searches inside the related table
    search_fields = ("title", "isbn", "category__name", "publisher__name")
    list_filter = ("category", "is_bestseller", "publisher")


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
    list_display = ("member_id", "full_name", "email", "birth_year", "city", "user", "registered_at")
    search_fields = ("full_name", "email", "city", "memberphone__phone")
    list_filter = ("city", "birth_year")
    inlines = [MemberPhoneInline]


@admin.register(MemberPhone)
class MemberPhoneAdmin(admin.ModelAdmin):
    list_display = ("member_phone_id", "member", "phone")
    search_fields = ("phone", "member__full_name")
    list_filter = ("member__city",)


@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ("librarian_id", "full_name", "email")
    search_fields = ("full_name", "email")
    list_filter = ("full_name",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("loan_id", "book", "member", "librarian",
                    "loan_date", "due_date", "return_date")
    search_fields = ("book__title", "member__full_name")
    list_filter = ("librarian", "loan_date", "due_date", "return_date")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("reservation_id", "book", "member", "status", "reserved_at")
    search_fields = ("book__title", "member__full_name")
    list_filter = ("status",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("review_id", "book", "member", "rating", "created_at")
    search_fields = ("book__title", "member__full_name", "comment")
    list_filter = ("rating",)
