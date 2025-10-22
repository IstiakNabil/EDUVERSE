# messaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Conversation, Message
from live.models import LiveClass, LiveClassEnrollment
from django.core.mail import send_mail # 👈 Import send_mail
from django.urls import reverse
from django.utils import timezone

@login_required
def start_conversation_view(request, class_pk):
    live_class = get_object_or_404(LiveClass, pk=class_pk)

    # Check if user is enrolled
    if not LiveClassEnrollment.objects.filter(user=request.user, live_class=live_class).exists():
        messages.error(request, "You must be enrolled to contact the instructor.")
        return redirect('live:live_class_detail', pk=class_pk)

    # Find or create a conversation
    conversation, created = Conversation.objects.get_or_create(
        live_class=live_class,
        student=request.user,
        defaults={'teacher': live_class.instructor}
    )
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)


@login_required
def inbox_view(request):
    conversations = Conversation.objects.filter(
        Q(student=request.user) | Q(teacher=request.user)
    ).order_by('-created_at')
    return render(request, 'messaging/inbox.html', {'conversations': conversations})


@login_required
def conversation_detail_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Authorization check
    if request.user != conversation.student and request.user != conversation.teacher:
        messages.error(request, "You are not authorized to view this conversation.")
        return redirect('messaging:inbox')

    # Handle sending a new message
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Check if this is the student's first message BEFORE creating the new one
            is_first_message = conversation.messages.filter(sender=conversation.student).count() == 0

            # Create the new message object
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )

            # ========================================
            #    EMAIL NOTIFICATION LOGIC
            # ========================================
            # Send an email only if the sender is the student AND it's their first message
            if message.sender == conversation.student and is_first_message:
                teacher = conversation.teacher
                subject = f"Message from {conversation.live_class.title}: {message.sender.username}"
                conversation_url = request.build_absolute_uri(
                    reverse('messaging:conversation_detail', kwargs={'conversation_id': conversation.id})
                )
                email_message = f"""
                            Hi {teacher.username},
                            You have a new message from {message.sender.username} regarding your live class "{conversation.live_class.title}".
                            View the conversation here: {conversation_url}
                            Thanks,
                            The Eduverse Team
                            """

                # Send the email
                send_mail(subject, email_message, None, [teacher.email], fail_silently=False)

                # Update the enrollment timestamp
                LiveClassEnrollment.objects.filter(
                    user=request.user,
                    live_class=conversation.live_class
                ).update(first_message_sent_at=timezone.now())
                return redirect('messaging:conversation_detail', conversation_id=conversation_id)

    # Mark messages as read by the current user
    messages_to_mark_read = conversation.messages.filter(is_read=False).exclude(sender=request.user)
    messages_to_mark_read.update(is_read=True)

    return render(request, 'messaging/conversation_detail.html', {'conversation': conversation})