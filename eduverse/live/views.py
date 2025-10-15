from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import LiveClassForm
from django.views.decorators.csrf import csrf_exempt
from live.models import LiveClass, LiveClassEnrollment
from django.utils import timezone
from datetime import timedelta
from .models import LiveClass, LiveClassRating
from .forms import LiveClassRatingForm

# Create a new live class
@login_required
def create_live_class(request):
    if request.method == 'POST':
        form = LiveClassForm(request.POST, request.FILES)
        if form.is_valid():
            live_class = form.save(commit=False)
            live_class.instructor = request.user
            live_class.save()
            return redirect('live:live_class_list')
    else:
        form = LiveClassForm()
    return render(request, 'live/create_live_class.html', {'form': form})


# Publicly viewable list of live classes
def live_class_list(request):
    classes = LiveClass.objects.all()
    return render(request, 'live/live_class_list.html', {'classes': classes})


# View a specific live class details
def live_class_detail(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)

    # 👇 ADD THIS LOGIC TO CHECK FOR ENROLLMENT 👇
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = LiveClassEnrollment.objects.filter(user=request.user, live_class=live_class).exists()

    context = {
        'live_class': live_class,
        'is_enrolled': is_enrolled,  # 👈 Pass the result to the template
    }
    return render(request, 'live/live_class_detail.html', context)


# Checkout page (similar to course checkout)
@login_required
def live_checkout(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)
    context = {
        'live_class': live_class,
    }
    return render(request, 'live/live_checkout.html', context)


# Manage live class (instructor only)
@login_required
def manage_live_class(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk, instructor=request.user)
    return render(request, 'live/manage_live_class.html', {'live_class': live_class})


# Edit a live class
@login_required
def edit_live_class(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk, instructor=request.user)
    if request.method == 'POST':
        form = LiveClassForm(request.POST, request.FILES, instance=live_class)
        if form.is_valid():
            form.save()
            return redirect('live:live_class_detail', pk=pk)
    else:
        form = LiveClassForm(instance=live_class)
    return render(request, 'live/edit_live_class.html', {'form': form, 'live_class': live_class})


# Delete a live class
@login_required
def delete_live_class(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk, instructor=request.user)
    if request.method == 'POST':
        live_class.delete()
        return redirect('live:live_class_list')
    return render(request, 'live/delete_live_class.html', {'live_class': live_class})


# Add video to a live class


@login_required
def live_payment_method(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)
    context = {
        'live_class': live_class,
    }
    return render(request, 'live/live_payment_method.html', context)

@login_required
def live_pay_wallet(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)
    context = {'live_class': live_class}
    return render(request, 'live/live_pay_wallet.html', context)


@login_required
def live_pay_card(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)
    context = {'live_class': live_class}
    return render(request, 'live/live_pay_card.html', context)

@login_required
@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payment_data = request.POST
        tran_id = payment_data.get('tran_id')

        try:
            # Check the prefix of the transaction ID
            parts = tran_id.split('_')
            product_type = parts[0]
            user_id = parts[1]
            product_id = parts[2]

            user = User.objects.get(pk=user_id)

            if product_type == 'course':
                course = Course.objects.get(pk=product_id)
                Enrollment.objects.get_or_create(
                    user=user, course=course, defaults={'amount_paid': course.price}
                )
                messages.success(request, f"Successfully enrolled in course: {course.title}")

            elif product_type == 'live':
                live_class = LiveClass.objects.get(pk=product_id)
                LiveClassEnrollment.objects.get_or_create(
                    user=user, live_class=live_class, defaults={'amount_paid': live_class.price}
                )
                messages.success(request, f"Successfully enrolled in live class: {live_class.title}")

            return render(request, 'payments/payment_success.html', {'payment_data': payment_data})

        except (IndexError, User.DoesNotExist, Course.DoesNotExist, LiveClass.DoesNotExist):
            messages.error(request, "Invalid transaction.")
            return render(request, 'payments/payment_fail.html')

    return render(request, 'payments/payment_fail.html')

@login_required
def my_live_classes_view(request):
    """
    Shows live classes a user has enrolled in within the last 3 days.
    """
    # Calculate the datetime for 3 days ago from now
    three_days_ago = timezone.now() - timedelta(days=3)

    # Filter enrollments for the current user that are newer than 3 days ago
    recent_enrollments = LiveClassEnrollment.objects.filter(
        user=request.user,
        enrolled_at__gte=three_days_ago
    ).order_by('-enrolled_at') # Show the newest first

    context = {
        'enrollments': recent_enrollments
    }
    return render(request, 'live/my_live_classes.html', context)

@login_required
def rate_live_class(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)
    enrollment = LiveClassEnrollment.objects.filter(user=request.user, live_class=live_class).first()

    # Check if user enrolled and 24 hours have passed
    if not enrollment:
        messages.error(request, "You must be enrolled to rate this live class.")
        return redirect('live:live_class_detail', pk=pk)

    time_passed = timezone.now() - enrollment.enrolled_at
    if time_passed.total_seconds() < 86400:  # 24 hours = 86400 seconds
        messages.error(request, "You can rate this live class only after 24 hours.")
        return redirect('live:live_class_detail', pk=pk)

    if request.method == 'POST':
        form = LiveClassRatingForm(request.POST)
        if form.is_valid():
            LiveClassRating.objects.update_or_create(
                user=request.user,
                live_class=live_class,
                defaults=form.cleaned_data
            )
            messages.success(request, "Your rating has been submitted.")
            return redirect('live:live_class_detail', pk=pk)
    else:
        form = LiveClassRatingForm()

    return render(request, 'live/rate_live_class.html', {'form': form, 'live_class': live_class})