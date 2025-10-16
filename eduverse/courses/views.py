from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CourseForm
from .forms import ModuleForm, VideoForm, TextContentForm
from .forms import ReviewForm
from django.contrib.contenttypes.models import ContentType
from .models import Module, CourseVideo, TextContent, Enrollment, UserProgress, Review
from django.db.models import Q
from .models import Course


def course_list(request):
    """Display all courses, with optional search and filtering."""
    queryset = Course.objects.all()
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    # If a search query is submitted
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # If a category is selected from the dropdown
    if category:
        queryset = queryset.filter(category=category)

    context = {
        'courses': queryset,
        'categories': Course.Category.choices,  # Pass all category choices to the template
        'current_query': query,
        'current_category': category,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    modules = course.modules.all().prefetch_related('videos', 'text_contents')
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    completed_content_ids = {}
    if request.user.is_authenticated:
        progress = UserProgress.objects.filter(user=request.user)
        completed_content_ids['text'] = {p.object_id for p in progress if p.content_type.model == 'textcontent'}
        completed_content_ids['video'] = {p.object_id for p in progress if p.content_type.model == 'coursevideo'}

    # --- Logic for unlocking modules ---
    unlocked = True
    for module in modules:
        module.is_unlocked = unlocked
        if unlocked:
            all_content_complete = True
            for video in module.videos.all():
                if video.id not in completed_content_ids['video']:
                    all_content_complete = False
                    break
            if not all_content_complete:
                unlocked = False
                continue

            for text in module.text_contents.all():
                if text.id not in completed_content_ids['text']:
                    all_content_complete = False
                    break
            unlocked = all_content_complete

    # --- Logic for allowing reviews ---
    can_review = False
    if is_enrolled:
        all_content_count = sum(m.videos.count() + m.text_contents.count() for m in modules)
        completed_count = len(completed_content_ids.get('text', [])) + len(completed_content_ids.get('video', []))
        if all_content_count > 0 and all_content_count == completed_count:
            if not course.reviews.filter(user=request.user).exists():
                can_review = True

    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'completed_content_ids': completed_content_ids,
        'review_form': ReviewForm(),
        'can_review': can_review,
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
def mark_as_complete_view(request, model_id, pk):
    content_type = get_object_or_404(ContentType, pk=model_id)
    model_class = content_type.model_class()
    content_object = get_object_or_404(model_class, pk=pk)
    UserProgress.objects.get_or_create(user=request.user, content_type=content_type, object_id=pk)
    if isinstance(content_object, (CourseVideo, TextContent)):
        return redirect('courses:course_detail', pk=content_object.module.course.pk)
    return redirect('home')

@login_required
def add_review_view(request, model_name, pk):
    content_type = get_object_or_404(ContentType, model=model_name)
    model_class = content_type.model_class()
    obj = get_object_or_404(model_class, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.content_object = obj
            review.save()
            messages.success(request, "Your review has been submitted. Thank you!")
    return redirect(obj.get_absolute_url())