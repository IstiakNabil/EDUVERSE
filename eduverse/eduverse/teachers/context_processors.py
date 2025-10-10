from .models import TeacherApplication

def teacher_status_context(request):
    """
    Makes the user's latest teacher application status available on all pages.
    """
    context = {}
    if request.user.is_authenticated:
        # Get the most recent application for the current user
        latest_app = TeacherApplication.objects.filter(user=request.user).order_by('-submitted_at').first()
        context['latest_teacher_app'] = latest_app
    return context