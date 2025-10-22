from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from courses.models import Course
from django.db.models import Q, Avg, F
from live.models import LiveClass

# Create your views here.
def home_view(request):
    """
    Handles both the default homepage and search results.
    For the homepage, it shows the top 5 rated courses, or the 5 latest if none have ratings.
    """
    query = request.GET.get('q', '')
    context = {'query': query}

    if query:
        # --- IF A SEARCH IS PERFORMED ---
        # Only fetch search results and set the search flag to True.
        search_results = Course.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        context['courses'] = search_results
        context['is_search'] = True # This is the crucial flag for the template
    else:
        # --- NEW Featured Courses Logic ---
        # 1. Primary: Try to get top 5 rated courses
        top_rated_courses = Course.objects.annotate(
            average_rating=Avg('reviews__rating')  # Calculate average rating
        ).filter(
            average_rating__isnull=False          # Exclude courses with no ratings
        ).order_by(
            '-average_rating'                     # Order by the highest rating first
        )[:5]

        # 2. Fallback: If no courses have ratings, get the 5 latest courses
        if top_rated_courses.exists():
            courses_to_display = top_rated_courses
            all_courses = Course.objects.annotate(
                average_rating=Avg('reviews__rating')
            ).order_by(
                F('average_rating').desc(nulls_last=True),  # Highest ratings first, unrated ones last
                '-created_at'  # Newest courses first among unrated ones
            )

            # 2. Chunk the sorted list into groups of 3 for the carousel
            chunk_size = 3
            courses_to_display = list(all_courses)
            chunked_courses = [courses_to_display[i:i + chunk_size] for i in
                               range(0, len(courses_to_display), chunk_size)]

            context['chunked_courses'] = chunked_courses
            context['is_search'] = False


            all_live_classes = LiveClass.objects.all().order_by('-created_at')
            # Chunk them into groups of 3 for the carousel
            live_classes_list = list(all_live_classes)
            chunked_live_classes = [live_classes_list[i:i + chunk_size] for i in
                                    range(0, len(live_classes_list), chunk_size)]

            # Add the chunked live classes to the context
            context['chunked_live_classes'] = chunked_live_classes

    return render(request, 'home.html', context)




class UserLoginView(LoginView):
    template_name = "accounts/login.html"

    def form_valid(self, form):
        """If the user is staff (admin), reject login on frontend."""
        if form.get_user().is_staff or form.get_user().is_superuser:
            messages.error(self.request, "Admins must log in through the admin portal.")
            return self.form_invalid(form)
        # Normal user continues as usual
        return super().form_valid(form)


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})




@login_required
def profile_view(request):
    # Block admins from accessing frontend profiles
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Admins cannot access the frontend profile.")

    # Get the latest teacher application for this user
    latest_app = request.user.teacher_applications.order_by("-submitted_at").first()

    if latest_app:
        if latest_app.status == "approved":
            messages.success(request, "✅ Congratulations! Your application has been approved.")
        elif latest_app.status == "rejected":
            messages.error(request, "❌ Unfortunately, your application has been rejected.")

    # Always return the page
    return render(request, "accounts/profile.html", {"latest_app": latest_app})
@login_required
def profile_update_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile_update.html', context)

@login_required
def delete_account_view(request):
    if request.method == "POST":
        user = request.user
        logout(request)             # log them out before deleting
        user.delete()               # delete the user from DB
        messages.success(request, "Your account has been deleted.")
        return redirect("home")     # send them somewhere safe
    return render(request, "accounts/delete_account.html")