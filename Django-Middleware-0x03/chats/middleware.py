import logging
import time
from datetime import datetime, time as dt_time
from django.http import HttpResponseForbidden

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler('requests.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class RequestLoggingMiddleware:
    """
    Logs each user's request with timestamp, user, and request path.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        logger.info(f"User: {user} - Path: {request.path}")
        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware:
    """
    Restricts access to the chat application outside 6 PM to 9 PM.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_time = datetime.now().time()
        start_time = dt_time(18, 0)  # 6 PM
        end_time = dt_time(21, 0)    # 9 PM

        if not (start_time <= current_time <= end_time):
            return HttpResponseForbidden("Access to the chat is restricted during this time.")

        return self.get_response(request)

class OffensiveLanguageMiddleware:
    """
    Limits the number of chat messages a user can send within a certain time window, based on their IP address.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_message_times = {}

    def __call__(self, request):
        if request.method == 'POST':
            ip = self.get_client_ip(request)
            now = time.time()
            window = 60  # 1 minute
            limit = 5

            times = self.ip_message_times.get(ip, [])
            # Remove timestamps older than 1 minute
            times = [t for t in times if now - t < window]

            if len(times) >= limit:
                return HttpResponseForbidden("Too many messages sent. Please wait a moment before sending more.")

            times.append(now)
            self.ip_message_times[ip] = times

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RolePermissionMiddleware:
    """
    Checks the user's role before allowing access to specific actions.
    Only users with 'admin' or 'moderator' roles are permitted.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden("Authentication required.")

        if not (user.is_staff or user.groups.filter(name__in=['admin', 'moderator']).exists()):
            return HttpResponseForbidden("You do not have permission to access this resource.")

        return self.get_response(request)
