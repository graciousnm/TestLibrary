from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Book, Rating, Borrow

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )

admin.site.register(Book)
admin.site.register(Rating)
admin.site.register(Borrow)