from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import gettext_lazy as _ # <<<--- ADD THIS IMPORT
from courses.models import Review

class LiveClass(models.Model):

    class LiveClassCategory(models.TextChoices):
        PROGRAMMING_TECH = 'programming-tech', _('Programming & Tech')
        BUSINESS = 'business', _('Business')
        DESIGN_CREATIVE = 'design-creative', _('Design & Creative')
        LIFESTYLE = 'lifestyle', _('Lifestyle')
        OTHER = 'other', _('Other')

    # --- Existing Fields ---
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='live_classes_taught')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    thumbnail = models.ImageField(upload_to='live_class_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # --- New Category Field ---
    category = models.CharField(
        max_length=50,
        choices=LiveClassCategory.choices,
        default=LiveClassCategory.OTHER
    )
    reviews = GenericRelation(Review, related_query_name='live_class')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Returns the URL for a specific live class instance.
        """
        # 'live' is the app_name from your live/urls.py
        # 'live_class_detail' is the name of the URL pattern for the detail view
        return reverse('live:live_class_detail', kwargs={'pk': self.pk})




class LiveClassEnrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    instructor_share = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    platform_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    first_message_sent_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        unique_together = ('user', 'live_class')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.live_class.title}"



