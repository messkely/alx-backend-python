import datetime
import time
import logging
from django.http import HttpResponseForbidden

# Configure logging
logging.basicConfig(
    filename='requests.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)

class RequestLoggingMiddleware:
    """
    Logs user requests with timestamp, user, and request path.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        logging.info(f"User: {user} - Path: {request.path}")
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    """
    Restricts chat access outside the allowed time window (9 AM to 6 PM).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.datetime.now().time()
        start_time = datetime.time(9, 0)
        end_time = datetime.time(18, 0)
        if now < start_time or now >= end_time:
            return HttpResponseForbidden("Access to the messaging app is only allowed between 9 AM and 6 PM.")
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Limits number of POST requests to 5 per minute per IP address.
    (Used to simulate offensive language prevention via rate limiting.)
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_message_log = {}

    def __call__(self, request):
        if request.method == 'POST':
            ip = self.get_client_ip(request)
            current_time = time.time()
            window_seconds = 60
            max_messages = 5

            timestamps = self.ip_message_log.get(ip, [])
            # Clean up timestamps older than 1 minute
            timestamps = [t for t in timestamps if current_time - t < window_seconds]

            if len(timestamps) >= max_messages:
                return HttpResponseForbidden("Rate limit exceeded. Please wait before sending more messages.")

            timestamps.append(current_time)
            self.ip_message_log[ip] = timestamps

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class RolePermissionMiddleware:
    """
    Allows only admin or moderator users to access certain resources.
    Returns 403 Forbidden for unauthorized users.
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
