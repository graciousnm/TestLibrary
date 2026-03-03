from django.urls import path
from library.views.book import *
from library.views.borrow import *
from library.views.rating import *
from library.views.user import RegisterUserView, AdminListUsers


urlpatterns = [
    # USER CREATION
    path('register/', RegisterUserView.as_view(), name='register'),
    #BOOK
    path('books/', PublicBookList.as_view(), name='all-books'),
    path('books/<int:pk>/borrow/', BorrowBook.as_view(), name='borrow-book'),
    path('borrows/', MyBorrows.as_view(), name='all-borrows'),
    path('borrows/<int:pk>/return/', ReturnBook.as_view(), name='return-book'),
    path('books/<int:pk>/rate/', RateBook.as_view(), name='rate-book'),


    # Author Urls
    path('author/books/', BooksByAuthor.as_view(), name='author-books'),
    path('author/book/<int:pk>/', BookDetailAuthor.as_view(), name='author-book-detail'),
    path('author/books/borrows/', MyBookBorrows.as_view(), name='author-borrowed-books'),
    path('author/books/ratings/', AuthorBookRating.as_view(), name='author-book-ratings'),

    # Admin Urls
    path('admin/books/', BookListAdmin.as_view(), name='admin-all-books'),
    path('admin/borrows/', AdminBookBorrows.as_view(), name='admin-all-borrows'),
    path('admin/ratings/', AdminBookRating.as_view(), name='admin-all-ratings'),
    path('admin/users/', AdminListUsers.as_view(), name='admin-all-users'),
]