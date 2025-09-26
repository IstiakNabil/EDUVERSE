from django.conf import settings
from django.db import models

class TeacherApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_applications"
    )
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    expertise = models.CharField(
        max_length=200,
        help_text="e.g., Physics, Calculus, IELTS"
    )
    years_experience = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    resume = models.FileField(upload_to="teacher_resumes/", blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]
        # ✅ No uniqueness constraints now

    def __str__(self):
        return f"{self.full_name} ({self.get_status_display()})"