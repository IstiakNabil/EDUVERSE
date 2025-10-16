# live/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LiveClassForm
from .models import LiveClass, LiveClassEnrollment
from django.utils import timezone
from datetime import timedelta
from courses.forms import ReviewForm
from django.db.models import Q

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

def live_class_list(request):
    """Displays all live classes, with an optional search filter."""
    queryset = LiveClass.objects.all()
    query = request.GET.get('q', '')

    # If a search query is submitted
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    context = {
        'classes': queryset,
        'current_query': query,
    }
    return render(request, 'live/live_class_list.html', context)


def live_class_detail(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)

    enrollment = None
    if request.user.is_authenticated:
        enrollment = LiveClassEnrollment.objects.filter(user=request.user, live_class=live_class).first()

    is_enrolled = enrollment is not None

    # --- This is the logic that needs to be correct ---
    can_review = False
    if is_enrolled:
        # Check if 2 minutes (for testing) have passed since the class start time
        if timezone.now() > live_class.start_time + timedelta(minutes=2):
            # Also check if the user has NOT already reviewed this class
            if not live_class.reviews.filter(user=request.user).exists():
                can_review = True

    context = {
        'live_class': live_class,
        'is_enrolled': is_enrolled,
        'review_form': ReviewForm(),
        'can_review': can_review,
    }
    return render(request, 'live/live_class_detail.html', context)

@login_required
def live_checkout(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)
    context = {'live_class': live_class}
    return render(request, 'live/live_checkout.html', context)

@login_required
def manage_live_class(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk, instructor=request.user)
    return render(request, 'live/manage_live_class.html', {'live_class': live_class})


def edit_live_class(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk, instructor=request.user)

    if request.method == 'POST':
        form = LiveClassForm(request.POST, request.FILES, instance=live_class)
        if form.is_valid():
            form.save()
            return redirect('live:live_class_detail', pk=pk)
    else:
        form = LiveClassForm(instance=live_class)

    # 👇 THIS RETURN STATEMENT WAS LIKELY MISSING OR MIS-INDENTED 👇
    return render(request, 'live/edit_live_class.html', {
        'form': form,
        'live_class': live_class
    })


@login_required
def delete_live_class(request, pk):
    # Get the live class, ensuring the person trying to delete it is the instructor
    live_class = get_object_or_404(LiveClass, pk=pk, instructor=request.user)

    # This block runs when the user clicks the final "Confirm Delete" button
    if request.method == 'POST':
        live_class.delete()
        messages.success(request, f"Live class '{live_class.title}' has been deleted.")
        return redirect('live:live_class_list')

    # This runs when the user first clicks the delete link, showing them a confirmation page
    context = {
        'live_class': live_class
    }
    return render(request, 'live/delete_live_class.html', context)

@login_required
def my_live_classes_view(request):
    three_days_ago = timezone.now() - timedelta(days=3)
    recent_enrollments = LiveClassEnrollment.objects.filter(
        user=request.user, enrolled_at__gte=three_days_ago
    ).order_by('-enrolled_at')
    context = {'enrollments': recent_enrollments}
    return render(request, 'live/my_live_classes.html', context)

# The old, unused views (live_payment_method, live_pay_wallet, live_pay_card)
# and the misplaced payment_success view have been removed.
@login_required
def manage_live_classes_view(request):
    """
    Lists all live classes created by the currently logged-in instructor.
    """
    # Get all live classes where the instructor is the current user
    instructor_classes = LiveClass.objects.filter(instructor=request.user)

    context = {
        'live_classes': instructor_classes,
    }
    return render(request, 'live/manage_live_classes.html', context)