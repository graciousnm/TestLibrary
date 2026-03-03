from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from library.serializers import UserCreationSerializer, UserPublicSerializer
from library.permissions import IsAdmin

User = get_user_model()
#-------------------------- User Creation  View -------------------------------#
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    # This must be Allow Any so people can sign up without being logged in!
    permission_classes = [AllowAny]

#--------------------------Admin sees all User -------------------------------#
class AdminListUsers(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = UserPublicSerializer
    def get_queryset(self):
        queryset = User.objects.exclude(pk=self.request.user.id)
        return queryset