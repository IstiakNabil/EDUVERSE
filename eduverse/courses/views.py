from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Course, CourseVideo, Enrollment
from .forms import CourseForm, VideoForm
from .models import Course, Module # 👈 Add Module
from .forms import ModuleForm, VideoForm, TextContentForm
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import CourseRating
from .forms import CourseRatingForm
from django.conf import settings
from .models import Course, CourseVideo, Enrollment, Module, CourseRating

def course_list(request):
    """Display all courses"""
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required
def course_detail(request, pk):
    """Display course details and module content"""
    course = get_object_or_404(Course, pk=pk)

    # videos = course.videos.all()  # 👈 1. REMOVE this incorrect and redundant line

    # This correctly gets all modules and their related content efficiently
    modules = course.modules.all().prefetch_related('videos', 'text_contents')

    # Check for enrollment status
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,  # 👈 2. ADD is_enrolled to the context
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


def category_view(request, category_name):
    """
    Filters and displays courses based on the selected category.
    """
    # This gets the human-readable name (e.g., "Programming & Tech") from the URL slug (e.g., "programming-tech")
    category_display_name = dict(Course.Category.choices).get(category_name)

    # Filter the courses that match the category
    courses_in_category = Course.objects.filter(category=category_name)

    context = {
        'courses': courses_in_category,
        'category_name': category_display_name,
    }
    return render(request, 'courses/category_page.html', context)


def sorry(request):
    return render(request, 'courses/sorry.html')


@login_required
def manage_courses_view(request):
    """
    Lists all courses created by the currently logged-in instructor.
    """
    # Ensure the user is an approved teacher
    latest_app = request.user.teacher_applications.order_by("-submitted_at").first()
    if not latest_app or latest_app.status != "approved":
        messages.error(request, "You are not authorized to manage courses.")
        return redirect("home")

    # Get all courses created by this user
    instructor_courses = Course.objects.filter(instructor=request.user)

    context = {
        'courses': instructor_courses,
    }
    return render(request, 'courses/manage_courses.html', context)

@login_required
def manage_course_content_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    # Authorization check: only the instructor can manage content
    if request.user != course.instructor:
        messages.error(request, "You are not authorized to manage this course.")
        return redirect('home')

    # Handle the form for creating a new module
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, f"Module '{module.title}' created successfully.")
            return redirect('courses:manage_course_content', course_pk=course.pk)
    else:
        form = ModuleForm()

    modules = course.modules.all()
    context = {
        'course': course,
        'modules': modules,
        'form': form,
    }
    return render(request, 'courses/manage_course_content.html', context)


@login_required
def add_video_view(request, module_pk):
    module = get_object_or_404(Module, pk=module_pk)
    course = module.course

    # Authorization check
    if request.user != course.instructor:
        messages.error(request, "You are not authorized to add content to this course.")
        return redirect('home')

    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.module = module
            video.save()
            messages.success(request, "Video added successfully.")
            return redirect('courses:manage_course_content', course_pk=course.pk)
    else:
        form = VideoForm()

    context = {
        'form': form,
        'content_type': 'Video',
        'module': module,
    }
    return render(request, 'courses/add_content_form.html', context)


@login_required
def add_text_content_view(request, module_pk):
    module = get_object_or_404(Module, pk=module_pk)
    course = module.course

    # Authorization check
    if request.user != course.instructor:
        messages.error(request, "You are not authorized to add content to this course.")
        return redirect('home')

    if request.method == 'POST':
        form = TextContentForm(request.POST)
        if form.is_valid():
            text_content = form.save(commit=False)
            text_content.module = module
            text_content.save()
            messages.success(request, "Text content added successfully.")
            return redirect('courses:manage_course_content', course_pk=course.pk)
    else:
        form = TextContentForm()

    context = {
        'form': form,
        'content_type': 'Text Content',
        'module': module,
    }
    return render(request, 'courses/add_content_form.html', context)



@login_required
def rate_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()

    # Only enrolled students can rate
    if not enrollment:
        messages.error(request, "You must be enrolled to rate this course.")
        return redirect('courses:course_detail', pk=pk)

    # Assume course is “finished” — you can later add a completion flag if needed.
    if request.method == 'POST':
        form = CourseRatingForm(request.POST)
        if form.is_valid():
            rating_obj, created = CourseRating.objects.update_or_create(
                user=request.user,
                course=course,
                defaults=form.cleaned_data
            )
            messages.success(request, "Your rating has been submitted.")
            return redirect('courses:course_detail', pk=pk)
    else:
        form = CourseRatingForm()

    return render(request, 'courses/rate_course.html', {'form': form, 'course': course})