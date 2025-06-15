from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User
from .models import Message

@login_required
@cache_page(60)  # Cache for 60 seconds
def conversation_list(request, user_id):
    """
    View to display messages in a conversation with caching
    """
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.get_conversation_messages(request.user, other_user)
    
    context = {
        'other_user': other_user,
        'messages': messages,
    }
    return render(request, 'chats/conversation.html', context)

@login_required
def unread_messages(request):
    """
    View to display unread messages using custom manager
    """
    unread_msgs = Message.unread.unread_for_user(request.user)
    
    context = {
        'unread_messages': unread_msgs,
        'unread_count': unread_msgs.count(),
    }
    return render(request, 'chats/unread.html', context)

@login_required
def threaded_conversation(request, message_id):
    """
    View to display a threaded conversation
    """
    root_message = get_object_or_404(Message, id=message_id)
    thread_messages = root_message.get_thread_messages()
    
    context = {
        'root_message': root_message,
        'thread_messages': thread_messages,
    }
    return render(request, 'chats/thread.html', context)