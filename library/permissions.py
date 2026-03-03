from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
            return(
                  request.user.is_authenticated and request.user.role == 'ADMIN'
            )
    
class IsAuthor(BasePermission):
      def has_permission(self, request, view):
            return(
                  request.user.is_authenticated and request.user.role == 'AUTHOR'
            )

class IsConsumer(BasePermission):
      def has_permission(self, request, view):
            return(
                  request.user.is_authenticated and request.user.role == 'CONSUMER'
            )