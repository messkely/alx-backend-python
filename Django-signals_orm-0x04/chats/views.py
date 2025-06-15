from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User
from django.db.models import Q, Prefetch
from django.core.cache import cache
from django.core.paginator import Paginator
from .models import Message

@login_required
@cache_page(60)  # Cache for 60 seconds
def conversation_list(request, user_id):
    """
    View to display messages in a conversation with caching and optimized queries
    """
    other_user = get_object_or_404(User, id=user_id)
    
    # Fully optimized conversation query
    messages_list = Message.get_conversation_messages(request.user, other_user)
    
    # Pagination
    paginator = Paginator(messages_list, 50)
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)
    
    context = {
        'other_user': other_user,
        'messages': messages_page,
    }
    return render(request, 'chats/conversation.html', context)

@login_required
def unread_messages(request):
    """
    View to display unread messages using custom manager with optimized queries
    """
    # Use custom manager with optimized queries
    unread_msgs = Message.unread.unread_for_user(request.user)
    
    # Pagination
    paginator = Paginator(unread_msgs, 25)
    page_number = request.GET.get('page')
    unread_page = paginator.get_page(page_number)
    
    context = {
        'unread_messages': unread_page,
        'unread_count': unread_msgs.count(),
    }
    return render(request, 'chats/unread.html', context)

@login_required
def threaded_conversation(request, message_id):
    """
    View to display a threaded conversation with optimized queries
    """
    root_message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        id=message_id
    )
    
    # Use optimized thread query method
    thread_messages = root_message.get_thread_messages()
    
    context = {
        'root_message': root_message,
        'thread_messages': thread_messages,
    }
    return render(request, 'chats/thread.html', context)

@login_required
def user_messages_dashboard(request):
    """
    Dashboard view showing user's sent and received messages with optimized queries
    """
    # Get sent messages with optimization
    sent_messages = Message.get_user_messages_optimized(
        request.user, 
        message_type='sent'
    )[:10]  # Limit to latest 10
    
    # Get received messages with optimization
    received_messages = Message.get_user_messages_optimized(
        request.user, 
        message_type='received'
    )[:10]  # Limit to latest 10
    
    # Get unread count efficiently
    unread_count = Message.unread.unread_for_user(request.user).count()
    
    context = {
        'sent_messages': sent_messages,
        'received_messages': received_messages,
        'unread_count': unread_count,
    }
    return render(request, 'chats/dashboard.html', context)

@login_required
def conversation_search(request):
    """
    Search conversations with optimized queries
    """
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Optimized search query
        results_list = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).filter(
            content__icontains=query
        ).select_related(
            'sender', 'receiver', 'parent_message'
        ).prefetch_related(
            Prefetch(
                'replies',
                queryset=Message.objects.select_related('sender', 'receiver')
            )
        ).order_by('-timestamp')
        
        # Pagination
        paginator = Paginator(results_list, 25)
        page_number = request.GET.get('page')
        results = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'results': results,
        'result_count': results.paginator.count if results else 0,
    }
    return render(request, 'chats/search.html', context)

