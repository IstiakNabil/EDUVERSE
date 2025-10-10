# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Course, Enrollment


@login_required
def checkout_page(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, "You are already enrolled in this course.")

        # FIX IS HERE: Use the correct namespaced URL name
        return redirect('courses:my_courses')

    return render(request, 'payments/checkout.html', {'course': course})

@login_required
def payment_selection(request, course_pk):
    """Displays the page with the two payment method buttons."""
    course = get_object_or_404(Course, pk=course_pk)
    return render(request, 'payments/payment_selection.html', {'course': course})

@login_required
def payment_form_mobile(request, course_pk):
    """Displays and processes the mobile payment form."""
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == 'POST':
        # This is where the enrollment happens
        Enrollment.objects.create(
            user=request.user,
            course=course,
            amount_paid=course.price
        )
        messages.success(request, f"You have successfully enrolled in '{course.title}'!")
        return redirect('payments:payment_success')
    return render(request, 'payments/payment_form_mobile.html', {'course': course})

@login_required
def payment_form_card(request, course_pk):
    """Displays and processes the bank/card payment form."""
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == 'POST':
        # This is where the enrollment happens
        Enrollment.objects.create(
            user=request.user,
            course=course,
            amount_paid=course.price
        )
        messages.success(request, f"You have successfully enrolled in '{course.title}'!")
        return redirect('payments:payment_success')
    return render(request, 'payments/payment_form_card.html', {'course': course})


@login_required
def payment_success(request):
    return render(request, 'payments/payment_success.html')