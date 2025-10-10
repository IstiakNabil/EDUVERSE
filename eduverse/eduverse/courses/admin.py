# courses/admin.py
from django.contrib import admin
from .models import Course, Module, CourseVideo, TextContent, Enrollment

# These "inlines" allow you to edit content directly within a Module
class CourseVideoInline(admin.TabularInline):
    model = CourseVideo
    extra = 1

class TextContentInline(admin.TabularInline):
    model = TextContent
    extra = 1

# This allows you to edit modules directly within a Course
class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'price', 'category', 'created_at']
    list_filter = ['category', 'instructor']
    search_fields = ['title', 'description']
    inlines = [ModuleInline] # Add modules directly to your course

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    inlines = [CourseVideoInline, TextContentInline] # Add videos/text to your modules

# You can also register the other models to see them separately
admin.site.register(Enrollment)
admin.site.register(CourseVideo)
admin.site.register(TextContent)