from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Course, CourseVideo, Enrollment
from .forms import CourseForm, VideoForm

def course_list(request):
    """Display all courses"""
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail(request, pk):
    """Display course details"""
    course = get_object_or_404(Course, pk=pk)
    videos = course.videos.all()
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    context = {
        'course': course,
        'videos': videos,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def course_create(request):
    latest_app = request.user.teacher_applications.order_by("-submitted_at").first()
    if not latest_app or latest_app.status != "approved":
        messages.error(
            request,
            "You must be an approved teacher before you can create courses."
        )
        return redirect("courses:sorry")

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            # This is the corrected part
            course = form.save(commit=False)  # 1. Create the object but don't save to the database yet.
            course.instructor = request.user  # 2. Set the current user as the instructor.
            course.save()  # 3. Now, save the fully updated object to the database.

            messages.success(request, 'Course created successfully!')
            return redirect('courses:course_detail', pk=course.pk)
    else:
        form = CourseForm()

    return render(request, 'courses/course_form.html', {
        'form': form,
        'title': 'Create New Course'
    })

@login_required
def course_edit(request, pk):
    """Edit an existing course"""
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('courses:course_detail', pk=course.pk)
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/course_form.html', {
        'form': form,
        'course': course,
        'title': 'Edit Course'
    })

@login_required
def course_delete(request, pk):
    """Delete a course"""
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('courses:course_list')

    return render(request, 'courses/course_confirm_delete.html', {'course': course})

@login_required
def add_videos(request, pk):
    """Add videos to a course"""
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.course = course
            video.save()
            messages.success(request, 'Video added successfully!')
            return redirect('courses:add_videos', pk=course.pk)
    else:
        form = VideoForm()

    videos = course.videos.all()
    return render(request, 'courses/add_videos.html', {
        'form': form,
        'course': course,
        'videos': videos
    })

@login_required
def enroll_course(request, pk):
    """
    This view's only job is to start the checkout process.
    It simply redirects the user to the checkout page in the 'payments' app.
    """
    # The 'course' object is only needed to get the pk for the redirect.
    course = get_object_or_404(Course, pk=pk)

    return redirect('payments:checkout', course_pk=course.pk)

@login_required
def my_courses(request):
    """Display all created courses"""
    courses = Course.objects.all()
    enrollments = Enrollment.objects.filter(user=request.user)
    return render(request, 'courses/my_courses.html', {'enrollments': enrollments})

def sorry(request):
    return render(request, 'courses/sorry.html')