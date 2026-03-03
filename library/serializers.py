from library.models import User, Book, Borrow, Rating
from rest_framework import serializers
from datetime import timedelta

#-------------------------- User Public Serializer -------------------------------#
class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'role']

#-------------------------- User Creation Serializer (WRITE, UPDATE) -------------------------------#
class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'email' : {'required': True},
            'role': {'required': False}
        }
    def validate_role(self, value):
            if value == User.Roles.ADMIN:
                raise serializers.ValidationError('You cannot create account as an Admin.')
            return value
        
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
#-------------------------- Book Public Serializer(READ) -------------------------------#
class BookPublicSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    class Meta:
        model = Book
        fields = ['id', 'title', 'description', 'author', 'is_available']

#-------------------------- Book Creation Serializer (WRITE, UPDATE) -------------------------------#
class BookCreationSerializer(serializers.ModelSerializer):
     class Meta:
        model = Book
        fields = ['title', 'description']

#-------------------------- Rating Public Serializer (READ)-------------------------------#
class RatingPublicSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    book = BookPublicSerializer(read_only=True)
    class Meta:
        model = Rating
        fields = ['id', 'user', 'book', 'score']

#-------------------------- Rating Creation Serializer (WRITE, UPDATE) -------------------------------#
class RatingCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['score']

#-------------------------- Borrow Public Serializer (READ) -------------------------------#
class BorrowPublicSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    book = BookPublicSerializer(read_only=True)
    due_date = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    class Meta:
        model = Borrow
        fields = ['id', 'book', 'user', 'borrowed_at', 'due_date', 'returned_at', 'is_overdue' ]

    def get_due_date(self, obj):
        return obj.borrowed_at + timedelta(days=14)
    
    def get_is_overdue(self, obj):
        from django.utils import timezone
        if not obj.returned_at:
            return timezone.now() > self.get_due_date(obj)
        return False

#-------------------------- Borrow Creation Serializer (WRITE, UPDATE) -------------------------------#
class BorrowCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['book']