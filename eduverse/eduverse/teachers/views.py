from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db import IntegrityError
from .forms import TeacherApplicationForm
from .models import TeacherApplication

@login_required
def apply_as_teacher(request):
    if request.method == "POST":
        form = TeacherApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            try:
                app.save()
            except IntegrityError:
                messages.error(request, "You already have a pending application.")
                return redirect("teachers:apply")
            messages.success(request, "Application submitted! An admin will review it.")
            return redirect("teachers:apply_success")
    else:
        # Pre-fill full_name/email from user if available
        initial = {}
        if request.user.is_authenticated:
            initial["full_name"] = getattr(request.user, "get_full_name", lambda: "")() or request.user.username
            initial["email"] = getattr(request.user, "email", "")
        form = TeacherApplicationForm(initial=initial)

    return render(request, "teachers/apply.html", {"form": form})

@login_required
def apply_success(request):
    # simple confirmation page
    return render(request, "teachers/apply_success.html")
