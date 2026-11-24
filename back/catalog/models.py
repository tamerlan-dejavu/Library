# Generated with "python manage.py inspectdb", then cleaned up.
# managed = False: the tables are created by db/schema.sql, not by migrations.
# Validators and clean() repeat the CHECK rules of schema.sql, so the admin
# shows a friendly form error instead of a database error page.
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models.functions import Now
from django.utils import timezone


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Publisher(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    name = models.TextField(unique=True)
    country = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "publisher"

    def __str__(self):
        return self.name


class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    full_name = models.TextField()
    birth_year = models.IntegerField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "author"

    def __str__(self):
        return self.full_name


class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.TextField()
    publication_year = models.IntegerField(blank=True, null=True)
    isbn = models.TextField(unique=True, blank=True, null=True)
    # on_delete copies the database rules: PROTECT = the FK has no ON DELETE
    # (NO ACTION), so Django refuses the delete with a clear admin message
    # instead of a database error; CASCADE = ON DELETE CASCADE in schema.sql
    category = models.ForeignKey(Category, models.PROTECT, blank=True, null=True)
    publisher = models.ForeignKey(Publisher, models.PROTECT, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cover_url = models.TextField(blank=True, null=True)
    is_bestseller = models.BooleanField(default=False)
    total_copies = models.IntegerField()
    available_copies = models.IntegerField()

    class Meta:
        managed = False
        db_table = "book"

    def __str__(self):
        return self.title

    def clean(self):
        # Same rule as CHECK (available_copies <= total_copies)
        if (self.available_copies is not None and self.total_copies is not None
                and self.available_copies > self.total_copies):
            raise ValidationError({"available_copies": "Available copies cannot be more than total copies."})


class BookAuthor(models.Model):
    book_author_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, models.CASCADE)
    author = models.ForeignKey(Author, models.PROTECT)

    class Meta:
        managed = False
        db_table = "book_author"
        unique_together = (("book", "author"),)

    def __str__(self):
        return f"{self.book} - {self.author}"


class Member(models.Model):
    member_id = models.AutoField(primary_key=True)
    # Optional link to a Django login account
    user = models.OneToOneField(User, models.SET_NULL, blank=True, null=True)
    full_name = models.TextField()
    email = models.TextField(unique=True, blank=True, null=True)
    birth_year = models.IntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2008)],
    )
    # Address (composite attribute) = city + street
    city = models.TextField(blank=True, null=True)
    street = models.TextField(blank=True, null=True)
    # db_default: let PostgreSQL fill the value (DEFAULT now() in schema.sql)
    registered_at = models.DateTimeField(blank=True, null=True, db_default=Now())

    class Meta:
        managed = False
        db_table = "member"

    def __str__(self):
        return self.full_name


class MemberPhone(models.Model):
    # Weak entity: a phone belongs to one member and is deleted with it
    member_phone_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, models.CASCADE)
    phone = models.TextField(validators=[RegexValidator(
        r"^\+?[0-9]{10,15}$", "Phone: optional + and 10-15 digits, e.g. +77011234567.",
    )])

    class Meta:
        managed = False
        db_table = "member_phone"
        unique_together = (("member", "phone"),)

    def __str__(self):
        return self.phone


class Librarian(models.Model):
    librarian_id = models.AutoField(primary_key=True)
    full_name = models.TextField()
    email = models.TextField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "librarian"

    def __str__(self):
        return self.full_name


class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, models.PROTECT, blank=True, null=True)
    member = models.ForeignKey(Member, models.PROTECT, blank=True, null=True)
    librarian = models.ForeignKey(Librarian, models.PROTECT, blank=True, null=True)
    loan_date = models.DateField(db_default=Now())
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "loan"

    def __str__(self):
        return f"{self.book} -> {self.member}"

    def clean(self):
        # Same rule as CHECK (due_date >= loan_date).
        # An empty loan_date becomes today in the database.
        loan_date = self.loan_date or timezone.localdate()
        if self.due_date is not None and self.due_date < loan_date:
            raise ValidationError({"due_date": "Due date cannot be before the loan date."})


class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, models.PROTECT, blank=True, null=True)
    member = models.ForeignKey(Member, models.PROTECT, blank=True, null=True)
    reserved_at = models.DateTimeField(blank=True, null=True, db_default=Now())
    status = models.TextField(db_default="pending")

    class Meta:
        managed = False
        db_table = "reservation"

    def __str__(self):
        return f"{self.book} ({self.status})"


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, models.CASCADE, blank=True, null=True)
    member = models.ForeignKey(Member, models.PROTECT, blank=True, null=True)
    # Same rule as CHECK (rating BETWEEN 1 AND 5)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True, db_default=Now())

    class Meta:
        managed = False
        db_table = "review"
        unique_together = (("book", "member"),)

    def __str__(self):
        return f"{self.book}: {self.rating}/5"
