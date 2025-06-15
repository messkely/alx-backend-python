from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent_messages'),
    path('conversation/<int:user_id>/', views.conversation_detail, name='conversation_detail'),
    path('notifications/', views.notifications, name='notifications'),
    path('thread/<int:message_id>/', views.message_thread, name='message_thread'),
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('delete-account/', views.delete_user, name='delete_user'),
]