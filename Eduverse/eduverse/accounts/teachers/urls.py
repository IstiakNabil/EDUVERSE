from django.urls import path
from . import views

app_name = "teachers"

urlpatterns = [
    path("apply/", views.apply_as_teacher, name="apply"),
    path("apply/success/", views.apply_success, name="apply_success"),
]
