from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from library.models import Rating, Book, Borrow
from library.serializers import RatingCreationSerializer, RatingPublicSerializer
from library.permissions import IsAuthor, IsAdmin
from django.shortcuts import get_object_or_404

#-------------------------- Pagination Class -------------------------------#
class RatingPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100

#-------------------------- Consumer Rating Book -------------------------------#
class RateBook(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        book = get_object_or_404(Book, pk=pk)

        has_borrowed = Borrow.objects.filter(book=book, user=user).exists()
        if not has_borrowed:
            return Response({'details':'You have to borrow and return book before you can rate.'}, status=status.HTTP_403_FORBIDDEN)

        has_not_returned = Borrow.objects.filter(book=book, user=user, returned_at__isnull=True).exists()
        if has_not_returned:
            return Response({'detail':'You must return the book before rating.'}, status=status.HTTP_403_FORBIDDEN)
        if Rating.objects.filter(book=book, user=user).exists():
            return Response({'detail':'You have already rated this book'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RatingCreationSerializer(data=request.data)
        if serializer.is_valid():
            rating_obj = serializer.save(user=user, book=book)
            return Response(RatingPublicSerializer(rating_obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#-------------------------- Author sees Rating Book -------------------------------#
class AuthorBookRating(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAuthor]
    pagination_class = RatingPagination
    serializer_class = RatingPublicSerializer

    def get_queryset(self):
        queryset = Rating.objects.filter(book__author=self.request.user).select_related('user', 'book').order_by('-id')
        return queryset

#-------------------------- Admin sees Rating Book -------------------------------#
class AdminBookRating(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = RatingPagination
    serializer_class = RatingPublicSerializer

    def get_queryset(self):
        queryset = Rating.objects.all().select_related('user', 'book').order_by('-id')
        return queryset
