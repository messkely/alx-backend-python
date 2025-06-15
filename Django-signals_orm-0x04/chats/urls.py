from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    path('conversation/<int:user_id>/', views.conversation_list, name='conversation_list'),
    path('unread/', views.unread_messages, name='unread_messages'),
    path('thread/<int:message_id>/', views.threaded_conversation, name='threaded_conversation'),
    path('dashboard/', views.user_messages_dashboard, name='dashboard'),
    path('search/', views.conversation_search, name='search'),
]
