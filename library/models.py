from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

#-------------------------- User Model -------------------------------#
class User(AbstractUser):
    class Roles(models.TextChoices):
            ADMIN = 'ADMIN', 'Admin',
            AUTHOR = 'AUTHOR', 'Author',
            CONSUMER = 'CONSUMER', 'Consumer'

    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.CONSUMER, db_index=True)
    
    def __str__(self):
        return self.get_full_name() or self.first_name
    
#-------------------------- Book Model -------------------------------#
class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['title', 'author', 'description'],
                name='unique_book_per_author_title_description'
            )
        ]

#-------------------------- Review Model -------------------------------#
class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.book.title} ({self.score} stars)'
    
#-------------------------- Borrow Model -------------------------------#
class Borrow(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrows')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_borrows')
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"