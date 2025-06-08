from datetime import datetime
import logging
import time
from django.http import HttpResponse
from django.core.cache import cache


def setup_request_logger():
    """Configure and return a logger for request tracking."""
    log = logging.getLogger(__name__)
    file_handler = logging.FileHandler('requests.log')
    log_format = logging.Formatter('%(message)s')
    file_handler.setFormatter(log_format)
    log.addHandler(file_handler)
    log.setLevel(logging.INFO)
    return log


REQUEST_LOGGER = setup_request_logger()


class RequestLoggingMiddleware:
    """Middleware to log incoming requests with user and path information."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        username = request.user if request.user.is_authenticated else 'Anonymous'
        REQUEST_LOGGER.info(f"{datetime.now()} - User: {username} - Path: {request.path}")
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    """Middleware to restrict access to business hours only."""
    
    BUSINESS_START = 9
    BUSINESS_END = 18
    RESTRICTION_MESSAGE = "Access restricted to business hours (9 AM - 6 PM)."
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_time = datetime.now().hour
        
        if self.BUSINESS_START <= current_time < self.BUSINESS_END:
            return self.get_response(request)
        
        return HttpResponse(
            self.RESTRICTION_MESSAGE,
            status=403,
            content_type="text/plain"
        )


class OffensiveLanguageMiddleware:
    """Middleware for rate limiting API conversations endpoint."""
    
    TIME_WINDOW = 60  # seconds
    RATE_LIMIT = 10   # requests per window
    API_PATH = '/api/conversations'
    RATE_LIMIT_MESSAGE = "Rate limit exceeded. Try again in a minute."
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not (request.path.startswith(self.API_PATH) and request.method == 'POST'):
            return None
            
        client_ip = request.META.get('REMOTE_ADDR')
        rate_key = f"rate-limit:{client_ip}"
        current_data = cache.get(rate_key, {"count": 0, "start": time.time()})
        
        time_elapsed = time.time() - current_data["start"]
        
        if time_elapsed > self.TIME_WINDOW:
            current_data = {"count": 1, "start": time.time()}
        else:
            current_data["count"] += 1
            
        if current_data["count"] > self.RATE_LIMIT:
            return HttpResponse(self.RATE_LIMIT_MESSAGE, status=429)
            
        cache.set(rate_key, current_data, timeout=self.TIME_WINDOW)
        return None


class RolepermissionMiddleware:
    """Middleware to enforce role-based access control."""
    
    ALLOWED_ROLES = {'admin', 'moderator'}
    ACCESS_DENIED_MESSAGE = "Access denied."
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.role in self.ALLOWED_ROLES:
            return self.get_response(request)
        
        return HttpResponse(
            self.ACCESS_DENIED_MESSAGE, 
            status=403, 
            content_type="text/plain"
        )