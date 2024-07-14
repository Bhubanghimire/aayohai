from django.contrib import admin
from accounts.models import User, PasswordReset


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'date_joined')
    list_filter = ('user_type',)


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('token', 'email', 'created_at')
