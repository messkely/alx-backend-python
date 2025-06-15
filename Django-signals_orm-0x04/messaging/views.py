from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Message
from .forms import MessageForm


@login_required
def inbox(request):
    """
    Display user's inbox with all messages.
    Shows unread count and highlights unread messages.
    """
    # Get all messages for the user with query optimization using .only()
    all_messages = Message.objects.filter(
        recipient=request.user
    ).select_related('sender').only(
        'id', 'subject', 'timestamp', 'read', 'sender__username', 'sender__first_name', 'sender__last_name'
    ).order_by('-timestamp')
    
    # Get unread messages count using custom manager
    unread_count = Message.unread.count_unread_for_user(request.user)
    
    # Pagination
    paginator = Paginator(all_messages, 20)
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)
    
    context = {
        'messages': messages_page,
        'unread_count': unread_count,
        'page_title': 'Inbox',
    }
    return render(request, 'messaging/inbox.html', context)


@login_required
def unread_messages(request):
    """
    Display only unread messages for the user using custom manager.
    Optimized with .only() to retrieve only necessary fields.
    """
    # Use custom manager to get unread messages with query optimization
    unread_msgs = Message.unread.unread_for_user(request.user).select_related('sender').only(
        'id', 'subject', 'timestamp', 'sender__username', 'sender__first_name', 'sender__last_name', 'body'
    ).order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(unread_msgs, 20)
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)
    
    context = {
        'messages': messages_page,
        'page_title': 'Unread Messages',
        'unread_count': unread_msgs.count(),
    }
    return render(request, 'messaging/unread_messages.html', context)


@login_required
def message_detail(request, message_id):
    """
    Display a specific message and mark it as read if it's unread.
    Uses query optimization with .only() and select_related().
    """
    message = get_object_or_404(
        Message.objects.select_related('sender', 'recipient').only(
            'id', 'subject', 'body', 'timestamp', 'read',
            'sender__username', 'sender__first_name', 'sender__last_name',
            'recipient__username'
        ),
        id=message_id,
        recipient=request.user
    )
    
    # Mark as read if it's unread
    if not message.read:
        message.mark_as_read()
        messages.success(request, 'Message marked as read.')
    
    context = {
        'message': message,
    }
    return render(request, 'messaging/message_detail.html', context)


@login_required
def compose_message(request):
    """
    Compose and send a new message.
    """
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('messaging:inbox')
    else:
        form = MessageForm()
    
    return render(request, 'messaging/compose.html', {'form': form})


@login_required
def mark_all_read(request):
    """
    Mark all unread messages as read for the current user using custom manager.
    """
    if request.method == 'POST':
        # Use custom manager method to mark all unread messages as read
        count = Message.unread.mark_all_read_for_user(request.user)
        messages.success(request, f'Marked {count} messages as read.')
    
    return redirect('messaging:inbox')


@login_required
def sent_messages(request):
    """
    Display messages sent by the user.
    Optimized with .only() to retrieve only necessary fields.
    """
    sent_msgs = Message.objects.filter(
        sender=request.user
    ).select_related('recipient').only(
        'id', 'subject', 'timestamp', 'read', 'recipient__username', 'recipient__first_name', 'recipient__last_name'
    ).order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(sent_msgs, 20)
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)
    
    context = {
        'messages': messages_page,
        'page_title': 'Sent Messages',
    }
    return render(request, 'messaging/sent_messages.html', context)


@login_required
def unread_count_api(request):
    """
    API endpoint to get unread messages count for the current user.
    Returns JSON response with unread count.
    """
    # Use custom manager to get unread count
    unread_count = Message.unread.count_unread_for_user(request.user)
    
    return JsonResponse({
        'unread_count': unread_count,
        'user': request.user.username
    })


@login_required
def latest_unread_messages(request):
    """
    Get the latest unread messages for the user.
    Uses custom manager method and query optimization.
    """
    # Use custom manager to get latest unread messages with optimization
    latest_unread = Message.unread.latest_unread_for_user(
        request.user, limit=5
    ).select_related('sender').only(
        'id', 'subject', 'timestamp', 'sender__username'
    )
    
    context = {
        'messages': latest_unread,
        'page_title': 'Latest Unread Messages',
    }
    return render(request, 'messaging/latest_unread.html', context)