from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Message, Notification

@login_required
def inbox(request):
    """
    View to display inbox messages with optimized queries
    """
    # Optimize query with select_related and prefetch_related
    messages_list = Message.objects.filter(
        receiver=request.user
    ).select_related(
        'sender', 'receiver', 'edited_by'
    ).prefetch_related(
        Prefetch(
            'replies',
            queryset=Message.objects.select_related('sender', 'receiver')
        )
    ).order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(messages_list, 20)
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)
    
    context = {
        'messages': messages_page,
        'message_count': messages_list.count(),
        'unread_count': messages_list.filter(read=False).count(),
    }
    return render(request, 'messaging/inbox.html', context)

@login_required
def sent_messages(request):
    """
    View to display sent messages with optimized queries
    """
    # Optimize query for sent messages
    messages_list = Message.objects.filter(
        sender=request.user
    ).select_related(
        'sender', 'receiver', 'edited_by'
    ).prefetch_related(
        Prefetch(
            'replies',
            queryset=Message.objects.select_related('sender', 'receiver')
        )
    ).order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(messages_list, 20)
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)
    
    context = {
        'messages': messages_page,
        'message_count': messages_list.count(),
    }
    return render(request, 'messaging/sent.html', context)

@login_required
def conversation_detail(request, user_id):
    """
    View to display conversation between current user and another user
    """
    other_user = get_object_or_404(User, id=user_id)
    
    # Optimized query for conversation messages
    messages_list = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).select_related(
        'sender', 'receiver', 'edited_by', 'parent_message'
    ).prefetch_related(
        Prefetch(
            'replies',
            queryset=Message.objects.select_related('sender', 'receiver')
        )
    ).order_by('timestamp')
    
    # Mark messages as read
    Message.objects.filter(
        sender=other_user, 
        receiver=request.user, 
        read=False
    ).update(read=True)
    
    # Pagination
    paginator = Paginator(messages_list, 50)
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)
    
    context = {
        'other_user': other_user,
        'messages': messages_page,
        'conversation_count': messages_list.count(),
    }
    return render(request, 'messaging/conversation.html', context)

@login_required
def notifications(request):
    """
    View to display user notifications with optimized queries
    """
    # Optimize notifications query
    notifications_list = Notification.objects.filter(
        user=request.user
    ).select_related(
        'user', 'message__sender', 'message__receiver'
    ).order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(notifications_list, 25)
    page_number = request.GET.get('page')
    notifications_page = paginator.get_page(page_number)
    
    context = {
        'notifications': notifications_page,
        'unread_count': notifications_list.filter(read=False).count(),
    }
    return render(request, 'messaging/notifications.html', context)

@login_required
def message_thread(request, message_id):
    """
    View to display a message thread with optimized queries
    """
    root_message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        id=message_id
    )
    
    # Get all messages in the thread with optimized queries
    thread_messages = Message.objects.filter(
        Q(parent_message=root_message) | Q(id=root_message.id)
    ).select_related(
        'sender', 'receiver', 'edited_by', 'parent_message'
    ).prefetch_related(
        Prefetch(
            'replies',
            queryset=Message.objects.select_related('sender', 'receiver')
        )
    ).order_by('timestamp')
    
    context = {
        'root_message': root_message,
        'thread_messages': thread_messages,
        'thread_count': thread_messages.count(),
    }
    return render(request, 'messaging/thread.html', context)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """
    AJAX view to mark a notification as read
    """
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            user=request.user
        )
        notification.read = True
        notification.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def delete_user(request):
    """
    View to delete user account and all related data
    """
    user = request.user
    username = user.username
    logout(request)  # Log out the user first
    user.delete()  # This will trigger the post_delete signal
    messages.success(request, f"Account '{username}' has been successfully deleted.")
    return redirect('home')

