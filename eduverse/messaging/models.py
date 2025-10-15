# messaging/models.py
from django.db import models
from django.conf import settings
from live.models import LiveClass

class Conversation(models.Model):
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='conversations')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_conversations')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('live_class', 'student') # One conversation per student per class

    def __str__(self):
        return f"Conversation for {self.live_class.title} between {self.student.username} and {self.teacher.username}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"