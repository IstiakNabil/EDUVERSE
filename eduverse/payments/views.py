# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import requests # Use the requests library directly
import uuid

from courses.models import Course, Enrollment
from live.models import LiveClass, LiveClassEnrollment
from django.contrib.auth.models import User

@login_required
def checkout_page(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    # ... (rest of this view is fine) ...
    return render(request, 'payments/checkout.html', {'course': course})


@login_required
def initiate_payment(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    api_url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"

    post_body = {
        'store_id': settings.STORE_ID,
        'store_passwd': settings.STORE_PASSWORD,
        'total_amount': str(course.price),
        'currency': "BDT",
        'tran_id': f"course_{request.user.id}_{course.pk}_{uuid.uuid4().hex[:6]}",
        'success_url': request.build_absolute_uri(reverse('payments:payment_success')),
        'fail_url': request.build_absolute_uri(reverse('payments:payment_fail')),
        'cancel_url': request.build_absolute_uri(reverse('payments:payment_cancel')),

        # Customer Information
        'cus_name': request.user.get_full_name() or request.user.username,
        'cus_email': request.user.email,

        # 👇 ADD THIS BLOCK OF CUSTOMER DETAILS 👇
        'cus_phone': request.user.profile.phone_number or '01700000000',
        'cus_add1': request.user.profile.location or 'Dhaka',
        'cus_city': request.user.profile.location or 'Dhaka',
        'cus_country': 'Bangladesh',

        # Product Information
        'product_name': course.title,
        'product_category': 'E-Learning Course',
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


@login_required
def initiate_live_class_payment(request, class_pk):
    live_class = get_object_or_404(LiveClass, pk=class_pk)
    api_url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"

    post_body = {
        'store_id': settings.STORE_ID,
        'store_passwd': settings.STORE_PASSWORD,
        'total_amount': str(live_class.price),
        'currency': "BDT",
        'tran_id': f"live_{request.user.id}_{live_class.pk}_{uuid.uuid4().hex[:6]}",
        'success_url': request.build_absolute_uri(reverse('payments:payment_success')),
        'fail_url': request.build_absolute_uri(reverse('payments:payment_fail')),
        'cancel_url': request.build_absolute_uri(reverse('payments:payment_cancel')),

        # Customer Information
        'cus_name': request.user.get_full_name() or request.user.username,
        'cus_email': request.user.email,

        # 👇 ADD THIS BLOCK OF CUSTOMER DETAILS 👇
        'cus_phone': request.user.profile.phone_number or '01700000000',
        'cus_add1': request.user.profile.location or 'Dhaka',
        'cus_city': request.user.profile.location or 'Dhaka',
        'cus_country': 'Bangladesh',

        # Product Information
        'product_name': live_class.title,
        'product_category': 'Live Class',
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

    return redirect('live:live_class_detail', pk=live_class.pk)

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payment_data = request.POST
        tran_id = payment_data.get('tran_id')
        try:
            parts = tran_id.split('_')
            product_type, user_id, product_id = parts[0], parts[1], parts[2]
            user = User.objects.get(pk=user_id)
            if product_type == 'course':
                course = Course.objects.get(pk=product_id)
                Enrollment.objects.get_or_create(user=user, course=course, defaults={'amount_paid': course.price})
                messages.success(request, f"Successfully enrolled in course: {course.title}")
            elif product_type == 'live':
                live_class = LiveClass.objects.get(pk=product_id)
                LiveClassEnrollment.objects.get_or_create(user=user, live_class=live_class, defaults={'amount_paid': live_class.price})
                messages.success(request, f"Successfully enrolled in live class: {live_class.title}")
            return render(request, 'payments/payment_success.html', {'payment_data': payment_data})
        except (IndexError, User.DoesNotExist, Course.DoesNotExist, LiveClass.DoesNotExist):
            messages.error(request, "Invalid transaction.")
            return render(request, 'payments/payment_fail.html')
    return render(request, 'payments/payment_fail.html')

@csrf_exempt
def payment_fail(request):
    messages.error(request, "Your payment has failed.")
    return render(request, 'payments/payment_fail.html')

@csrf_exempt
def payment_cancel(request):
    messages.warning(request, "Your payment was canceled.")
    return render(request, 'payments/payment_fail.html')