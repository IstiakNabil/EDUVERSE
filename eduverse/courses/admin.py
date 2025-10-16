# courses/admin.py
from django.contrib import admin
from .models import Course, Module, CourseVideo, TextContent, Enrollment, UserProgress, Review

# Inlines for a better admin experience
class CourseVideoInline(admin.TabularInline):
    model = CourseVideo
    extra = 1

class TextContentInline(admin.TabularInline):
    model = TextContent
    extra = 1

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'price', 'category', 'created_at']
    list_filter = ['category', 'instructor']
    search_fields = ['title', 'description']
    inlines = [ModuleInline] # Lets you add Modules directly on the Course page

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title']
    inlines = [CourseVideoInline, TextContentInline] # Lets you add content from the Module page

# Register the remaining models to make them visible in the admin
admin.site.register(UserProgress) # 👈 ADD THIS
admin.site.register(Review)       # 👈 ADD THIS

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'amount_paid', 'platform_fee', 'enrolled_at')
    list_filter = ('enrolled_at', 'course')