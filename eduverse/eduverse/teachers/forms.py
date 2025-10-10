from django import forms
from .models import TeacherApplication

class TeacherApplicationForm(forms.ModelForm):
    class Meta:
        model = TeacherApplication
        fields = ["full_name", "email", "expertise", "years_experience", "bio", "linkedin_url", "resume"]
