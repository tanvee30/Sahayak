from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, EmailOTP


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "email",
        "username",
        "role",
        "is_verified",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("email", "username")
    ordering = ("email",)


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("email", "code", "purpose", "used", "created_at", "expires_at")
    search_fields = ("email", "code")
    list_filter = ("purpose", "used")