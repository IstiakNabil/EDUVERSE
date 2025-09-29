from django.contrib import admin
from .models import Course, CourseVideo, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'created_at']  # Removed 'creator'
    list_filter = ['created_at', 'price']
    search_fields = ['title', 'description']

@admin.register(CourseVideo)
class CourseVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'created_at']
    list_filter = ['created_at']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['course', 'amount_paid', 'enrolled_at']  # Removed 'student'
    list_filter = ['enrolled_at']