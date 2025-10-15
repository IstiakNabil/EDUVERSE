from django.urls import path
from . import views

app_name = 'live'

urlpatterns = [
    # Class creation and listing
    path('create-live-class/', views.create_live_class, name='create_live_class'),
    path('live-classes/', views.live_class_list, name='live_class_list'),

    # Class detail and checkout
    path('live-classes/<int:pk>/', views.live_class_detail, name='live_class_detail'),
    path('live-classes/<int:pk>/checkout/', views.live_checkout, name='live_checkout'),

    # Instructor management URLs
    path('live-classes/<int:pk>/manage/', views.manage_live_class, name='manage_live_class'),
    path('live-classes/<int:pk>/edit/', views.edit_live_class, name='edit_live_class'),
    path('live-classes/<int:pk>/delete/', views.delete_live_class, name='delete_live_class'),

    path('my-live-classes/', views.my_live_classes_view, name='my_live_classes'),
    # The following old payment URLs are no longer needed and have been removed:
    # - live_payment_method
    # - live_pay_wallet
    # - live_pay_card
    # - live_payment_success
    path('<int:pk>/rate/', views.rate_live_class, name='rate_live_class'),

]