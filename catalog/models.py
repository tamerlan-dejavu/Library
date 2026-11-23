# Generated with "python manage.py inspectdb", then cleaned up.
# managed = False: the tables are created by db/schema.sql, not by migrations.
from django.contrib.auth.models import User
from django.db import models


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
    # DO_NOTHING: the database itself decides what happens on delete
    category = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    publisher = models.ForeignKey(Publisher, models.DO_NOTHING, blank=True, null=True)
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


class BookAuthor(models.Model):
    book_author_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, models.DO_NOTHING)
    author = models.ForeignKey(Author, models.DO_NOTHING)

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
    birth_year = models.IntegerField(blank=True, null=True)
    registered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "member"

    def __str__(self):
        return self.full_name


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
    book = models.ForeignKey(Book, models.DO_NOTHING, blank=True, null=True)
    member = models.ForeignKey(Member, models.DO_NOTHING, blank=True, null=True)
    librarian = models.ForeignKey(Librarian, models.DO_NOTHING, blank=True, null=True)
    loan_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "loan"

    def __str__(self):
        return f"{self.book} -> {self.member}"


class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, models.DO_NOTHING, blank=True, null=True)
    member = models.ForeignKey(Member, models.DO_NOTHING, blank=True, null=True)
    reserved_at = models.DateTimeField(blank=True, null=True)
    status = models.TextField()

    class Meta:
        managed = False
        db_table = "reservation"

    def __str__(self):
        return f"{self.book} ({self.status})"


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, models.DO_NOTHING, blank=True, null=True)
    member = models.ForeignKey(Member, models.DO_NOTHING, blank=True, null=True)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "review"
        unique_together = (("book", "member"),)

    def __str__(self):
        return f"{self.book}: {self.rating}/5"
