# messaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Conversation, Message
from live.models import LiveClass, LiveClassEnrollment
from django.core.mail import send_mail # 👈 Import send_mail
from django.urls import reverse

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

    # Authorization: ensure user is part of this conversation
    if request.user != conversation.student and request.user != conversation.teacher:
        messages.error(request, "You are not authorized to view this conversation.")
        return redirect('messaging:inbox')

    # Handle sending a new message
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            return redirect('messaging:conversation_detail', conversation_id=conversation_id)

    # Mark messages as read
    messages_to_mark_read = conversation.messages.filter(is_read=False).exclude(sender=request.user)
    messages_to_mark_read.update(is_read=True)

    return render(request, 'messaging/conversation_detail.html', {'conversation': conversation})