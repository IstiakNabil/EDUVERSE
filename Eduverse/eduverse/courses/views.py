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

    context = {
        'course': course,
        'videos': videos,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def course_create(request):
    """Create a new course"""
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
            course = form.save(commit=False)
            course.instructor = request.user  # <<< CHANGED
            course.save()
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

    # Ownership check
    if course.instructor != request.user:  # <<< CHANGED
        messages.error(request, "You do not have permission to edit this course.")
        return redirect('courses:course_list')

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

    # Ownership check
    if course.instructor != request.user:  # <<< CHANGED
        messages.error(request, "You do not have permission to delete this course.")
        return redirect('courses:course_list')

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('courses:course_list')

    return render(request, 'courses/course_confirm_delete.html', {'course': course})


@login_required
def add_videos(request, pk):
    """Add videos to a course"""
    course = get_object_or_404(Course, pk=pk)

    # Ownership check
    if course.instructor != request.user:  # <<< CHANGED
        messages.error(request, "You do not have permission to add videos to this course.")
        return redirect('courses:course_list')

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
    """Enroll in a course"""
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        # Create enrollment (simplified without user)
        enrollment = Enrollment.objects.create(
            course=course,
            user=request.user,
            amount_paid=course.price
        )
        messages.success(request, f'Successfully enrolled in {course.title}!')
        return redirect('courses:course_detail', pk=pk)

    return render(request, 'courses/enroll_confirm.html', {'course': course})


@login_required
def my_courses(request):
    """Display all created courses"""
    courses = Course.objects.filter(instructor=request.user)  # <<< CHANGED
    return render(request, 'courses/my_courses.html', {'courses': courses})


def sorry(request):
    return render(request, 'courses/sorry.html')