from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_user(request):
    """
    View to delete user account and all related data
    """
    user = request.user
    logout(request)  # Log out the user first
    user.delete()  # This will trigger the post_delete signal
    messages.success(request, "Your account has been successfully deleted.")
    return redirect('home')