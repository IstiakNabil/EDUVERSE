from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from courses.models import Review  # Import the generic Review model


class LiveClass(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='live_class_thumbnails/', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    # Best practice is to use settings.AUTH_USER_MODEL
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # 👇 ADD THIS FIELD (used for the review logic)
    start_time = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    # 👇 ADD THIS RELATION to connect to the Review model
    reviews = GenericRelation(Review)

    # 👇 ADD THIS METHOD for creating clean URLs
    def get_absolute_url(self):
        return reverse('live:live_class_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


class LiveClassEnrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('user', 'live_class')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.live_class.title}"