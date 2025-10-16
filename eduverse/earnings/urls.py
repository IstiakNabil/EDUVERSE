from django.urls import path
from . import views

app_name = 'earnings'
urlpatterns = [
    path('', views.earnings_view, name='earnings_page'),
]