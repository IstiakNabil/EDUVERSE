# messaging/urls.py
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # A page to start a conversation from the live class detail page
    path('start/<int:class_pk>/', views.start_conversation_view, name='start_conversation'),
    # The user's main inbox showing all their conversations
    path('inbox/', views.inbox_view, name='inbox'),
    # The detail view for a single conversation thread
    path('conversation/<int:conversation_id>/', views.conversation_detail_view, name='conversation_detail'),
]