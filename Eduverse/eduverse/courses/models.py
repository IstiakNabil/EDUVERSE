from django.db import models
from django.urls import reverse
from django.conf import settings

class Course(models.Model):

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('courses:course_detail', kwargs={'pk': self.pk})


class CourseVideo(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='course_videos/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


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