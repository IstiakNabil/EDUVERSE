from django.db import models
from django.urls import reverse
from django.conf import settings

class Course(models.Model):
    class Category(models.TextChoices):
        PROGRAMMING = 'programming-tech', 'Programming & Tech'
        GRAPHICS = 'graphics-design', 'Graphics & Design'
        MARKETING = 'digital-marketing', 'Digital Marketing'
        WRITING = 'writing-translation', 'Writing & Translation'
        VIDEO = 'video-animation', 'Video & Animation'
        OTHER = 'other', 'Other'

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        null = True,
        blank = True
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.OTHER
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('courses:course_detail', kwargs={'pk': self.pk})

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0) # To order modules within a course

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.title}"


class CourseVideo(models.Model):
    # Change the ForeignKey from Course to Module
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='course_videos/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title
class TextContent(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='text_contents')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
                unique_together = ('user', 'course')

    def __str__(self):
        # Let's make this more informative
        return f"{self.user.username} enrolled in {self.course.title}"