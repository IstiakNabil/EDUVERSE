from django.contrib import admin
from .models import Course, CourseVideo, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    # Add 'instructor' to see who created the course
    list_display = ['title', 'instructor', 'price', 'created_at']
    list_filter = ['created_at', 'price', 'instructor'] # Also good to filter by instructor
    search_fields = ['title', 'description']

@admin.register(CourseVideo)
class CourseVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'created_at']
    list_filter = ['created_at']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    # Add 'user' to see who is enrolled
    list_display = ['user', 'course', 'amount_paid', 'enrolled_at']
    list_filter = ['enrolled_at', 'user'] # Also good to filter by user