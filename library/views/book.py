from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from library.permissions import IsAuthor, IsAdmin
from library.models import Book
from library.serializers import BookPublicSerializer, BookCreationSerializer
from django.db import transaction, IntegrityError
from django.db.models import Value
from django.shortcuts import get_object_or_404
from django.db.models.functions import Concat

#-------------------------- Pagination Class -------------------------------#
class BookPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100

#-------------------------- List Books View (No Authentication) -------------------------------#
class PublicBookList(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookPublicSerializer
    pagination_class = BookPagination

#-------------------------- List Books View (Author Only) -------------------------------#
class BooksByAuthor(APIView):
    permission_classes = [IsAuthor]

    # Viewing all my book (author)
    def get(self, request):
        books = Book.objects.filter(author=request.user).order_by('-id')
        paginator = BookPagination()
        paginated_books = paginator.paginate_queryset(books, request)
        if paginated_books is not None:
            serializer = BookPublicSerializer(paginated_books, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = BookPublicSerializer(books, many=True) # This will be my fallback
        return Response(serializer.data)
    
    # Creating a new book
    def post(self, request):
        serializer = BookCreationSerializer(data=request.data)
        if serializer.is_valid():
                try:
                    with transaction.atomic():
                        book = serializer.save(author=request.user)
                except IntegrityError:
                    return Response({'detail':'You have already created this book.'}, status=status.HTTP_400_BAD_REQUEST)
                return Response(BookPublicSerializer(book).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#-------------------------- List Books View (Author Only) -------------------------------#
class BookDetailAuthor(APIView):
    permission_classes = [IsAuthor]

    # Get a book detail
    def get(self, request, pk):
        book_detail = get_object_or_404(Book, author=request.user, pk=pk)
        serializer = BookPublicSerializer(book_detail)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Updating my existing book
    def put(self, request, pk):
        book = get_object_or_404(Book, pk=pk, author=request.user)
        serializer = BookCreationSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    serializer.save()
            except IntegrityError:
                return Response({'details':'You already have a book with this title and description'})
            return Response(BookPublicSerializer(book).data, status=status.HTTP_200_OK)
            
    def delete(self, request, pk):
        book = get_object_or_404(Book, author=request.user, pk=pk)
        if not book.is_available:
            return Response({'details':'You cannot delete a borrowed book'}, status=status.HTTP_400_BAD_REQUEST)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#-------------------------- List Books View (Admin Only) -------------------------------#
class BookListAdmin(generics.ListAPIView):
    permission_classes = [IsAdmin]
    def get_queryset(self):
        return Book.objects.annotate(author_full_name=Concat('author__first_name', Value(' '), 
                'author__last_name')).all().order_by('-id')
    serializer_class = BookPublicSerializer
    pagination_class = BookPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_available', 'author']
    search_fields = ['title', 'description', 'author__username', 'author__first_name']