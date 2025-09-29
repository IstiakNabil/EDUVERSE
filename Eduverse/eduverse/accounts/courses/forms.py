from django import forms
from .models import Course, CourseVideo

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'thumbnail', 'price']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your course'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

class VideoForm(forms.ModelForm):
    class Meta:
        model = CourseVideo
        fields = ['title', 'video_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Video title'
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }