# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import requests  # 👈 Import the requests library
import uuid
from django.contrib.auth import login
from courses.models import Course, Enrollment
from django.contrib.auth.models import User


@login_required
def checkout_page(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, "You are already enrolled in this course.")
        return redirect('courses:my_courses')
    return render(request, 'payments/checkout.html', {'course': course})


@login_required
# payments/views.py

@login_required
def initiate_payment(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    api_url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"

    post_body = {
        'store_id': settings.STORE_ID,
        'store_passwd': settings.STORE_PASSWORD,
        'total_amount': str(course.price),
        'currency': "BDT",
        'tran_id': f"{request.user.id}_{course.pk}_{uuid.uuid4().hex[:6]}",
        'success_url': request.build_absolute_uri(reverse('payments:payment_success')),
        'fail_url': request.build_absolute_uri(reverse('payments:payment_fail')),
        'cancel_url': request.build_absolute_uri(reverse('payments:payment_cancel')),

        # Customer info
        'cus_name': request.user.get_full_name() or request.user.username,
        'cus_email': request.user.email,
        'cus_add1': 'Dhaka',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',

        # 👇 THIS IS THE UPDATED LINE 👇
        'cus_phone': request.user.profile.phone_number or '01700000000',  # Use number from profile or a default

        # Product info
        'product_name': course.title,
        'product_category': 'E-Learning',
        'product_profile': 'general',
        'shipping_method': 'NO',
    }

    try:
        response = requests.post(api_url, data=post_body)
        response_json = response.json()

        if response_json.get('status') == 'SUCCESS':
            return redirect(response_json.get('GatewayPageURL'))
        else:
            messages.error(request, f"Gateway Error: {response_json.get('failedreason', 'Unknown error')}")
    except Exception as e:
        messages.error(request, f"Could not connect to payment gateway. Error: {e}")

    return redirect('courses:course_detail', pk=course.pk)


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payment_data = request.POST
        tran_id = payment_data.get('tran_id')

        try:
            # Extract user_id and course_id from transaction ID
            parts = tran_id.split('_')
            user_id = parts[0]
            course_id = parts[1]

            user = User.objects.get(pk=user_id)
            course = Course.objects.get(pk=course_id)

            # ✅ Log the user back in (restores session)
            login(request, user)

            # Enroll user if not already enrolled
            Enrollment.objects.get_or_create(
                user=user,
                course=course,
                defaults={'amount_paid': course.price}
            )

            return render(request, 'payments/payment_success.html', {'payment_data': payment_data})

        except (IndexError, User.DoesNotExist, Course.DoesNotExist):
            messages.error(request, "Invalid transaction.")
            return render(request, 'payments/payment_fail.html', {'message': 'Invalid transaction data.'})

    # If not a POST request
    return render(request, 'payments/payment_fail.html', {'message': 'Invalid request method.'})


@csrf_exempt
def payment_fail(request):
    messages.error(request, "Your payment has failed. Please try again.")
    return render(request, 'payments/payment_fail.html')


@csrf_exempt
def payment_cancel(request):
    messages.warning(request, "Your payment was canceled.")
    return render(request, 'payments/payment_fail.html', {'message': 'Your payment was canceled.'})