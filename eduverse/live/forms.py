from django import forms
from .models import LiveClass
from .models import LiveClassRating

class LiveClassForm(forms.ModelForm):
    class Meta:
        model = LiveClass
        fields = ['title', 'description', 'scheduled_at']

class LiveClassRatingForm(forms.ModelForm):
    class Meta:
        model = LiveClassRating
        fields = ['rating', 'review']