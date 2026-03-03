from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from library.models import Borrow, Book
from library.serializers import BorrowPublicSerializer
from library.permissions import IsAuthor, IsAdmin
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

#-------------------------- Pagination Class -------------------------------#
class BorrowPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

#-------------------------- Consumer Sees Borrowed Book -------------------------------#
class MyBorrows(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = BorrowPagination
    serializer_class = BorrowPublicSerializer
    
    def get_queryset(self):
        queryset = Borrow.objects.filter(user=self.request.user)
        return queryset

#-------------------------- Consumer Borrows Book -------------------------------#
class BorrowBook(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        try:
            with transaction.atomic():
                book = get_object_or_404(Book.objects.select_for_update(), pk=pk)

                # Block Admins
                if user.role == 'ADMIN':
                    return Response({'detail':'Admins are not allowed to borrow books.'}, status=status.HTTP_400_BAD_REQUEST)
                # Block Author who owns this book
                if book.author == user:
                    return Response({'details':'Sorry, you cannot borrow your own book.'}, status=status.HTTP_400_BAD_REQUEST)
                # If book is not available
                if not book.is_available:
                    return Response({'details':'Sorry, this book is not available.'}, status=status.HTTP_400_BAD_REQUEST)
                # If user has borrowed more than 3 books
                if Borrow.objects.filter(user=user, returned_at__isnull=True).count() >= 3:
                    return Response({'details':'Sorry, you have reaced maximum book borrows.'}, status=status.HTTP_400_BAD_REQUEST)
                
                book.is_available = False
                book.save()
                new_record = Borrow.objects.create(user=user, book=book)
                serializer = BorrowPublicSerializer(new_record, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({'details':'Internal error.'}, status=500)
        
#-------------------------- Consumer Returns Book -------------------------------#
class ReturnBook(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        user = request.user
        try:
            with transaction.atomic():
                borrowed_record = Borrow.objects.select_for_update().filter(book_id=pk, user=user, returned_at__isnull=True).first()
                if not borrowed_record:
                    return Response({'detail':'No active record found for this book.'}, status=status.HTTP_404_NOT_FOUND)
                book = borrowed_record.book
                book.is_available = True
                book.save()

                borrowed_record.returned_at = timezone.now()
                borrowed_record.save()

                serializer = BorrowPublicSerializer(borrowed_record)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'details':f'Internal error {str(e)}'}, status=500)
        
#-------------------------- Author Books Being Borrowed -------------------------------#
class MyBookBorrows(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAuthor]
    pagination_class = BorrowPagination
    serializer_class = BorrowPublicSerializer
    
    def get_queryset(self):
        # We add select_related to "join" the user and book tables in one query
        return Borrow.objects.filter(
            book__author=self.request.user
        ).select_related('user', 'book').order_by('-borrowed_at')

#-------------------------- Admin sees Books Being Borrowed -------------------------------#
class AdminBookBorrows(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = BorrowPublicSerializer
    pagination_class = BorrowPagination

    def get_queryset(self):
        queryset = Borrow.objects.all().select_related('user', 'book')
        
        # Look for a query parameter like ?overdue=true
        is_overdue = self.request.query_params.get('overdue')
        
        if is_overdue == 'true':
            # Calculate the date that was 14 days ago
            limit_date = timezone.now() - timedelta(days=14)
            # Filter for books not returned AND borrowed before that limit
            queryset = queryset.filter(returned_at__isnull=True, borrowed_at__lt=limit_date)
        return queryset.order_by('-borrowed_at')