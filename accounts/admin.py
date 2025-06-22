from django.contrib import admin
from accounts.models import User, OTP, Advertise, About


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id',  'first_name', 'last_name', 'email', 'gender', 'date_joined')
    list_filter = ('user_type',)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('otp', 'email', 'created_at')


@admin.register(Advertise)
class AdvertiseAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad', 'created_at')


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
