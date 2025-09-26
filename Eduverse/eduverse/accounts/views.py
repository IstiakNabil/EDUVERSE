from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import CustomUserCreationForm
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
# Create your views here.

from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

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
def home_view(request):
    return render(request, 'home.html')


@login_required
def profile_view(request):
    # Block admins from accessing frontend profiles
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Admins cannot access the frontend profile.")

    # Get the latest teacher application for this user
    latest_app = request.user.teacher_applications.order_by("-submitted_at").first()

    # If approved, show a success notification
    if latest_app and latest_app.status == "approved":
        messages.success(request, "✅ Congratulations! Your application has been approved.")

    # Pass latest_app into the template!
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