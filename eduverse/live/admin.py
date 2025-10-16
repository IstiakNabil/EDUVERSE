# live/admin.py
from django.contrib import admin
from .models import LiveClass, LiveClassEnrollment

@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'start_time')
    list_filter = ('start_time', 'instructor')
    search_fields = ('title', 'description')

@admin.register(LiveClassEnrollment)
class LiveClassEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'live_class', 'amount_paid', 'platform_fee', 'enrolled_at')
    list_filter = ('enrolled_at', 'live_class')
    search_fields = ('user__username', 'live_class__title')