from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Page 1: The initial checkout summary
    path('checkout/<int:course_pk>/', views.checkout_page, name='checkout'),

    # Page 2: The new payment method selection page
    path('select/<int:course_pk>/', views.payment_selection, name='payment_selection'),

    # Page 3A: The form for mobile wallet payments
    path('form/mobile/<int:course_pk>/', views.payment_form_mobile, name='payment_form_mobile'),

    # Page 3B: The form for bank/card payments
    path('form/card/<int:course_pk>/', views.payment_form_card, name='payment_form_card'),

    # The final success page
    path('success/', views.payment_success, name='payment_success'),
]