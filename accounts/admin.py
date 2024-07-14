from django.contrib import admin
from accounts.models import User, OTP


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'date_joined')
    list_filter = ('user_type',)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('otp', 'email', 'created_at')
