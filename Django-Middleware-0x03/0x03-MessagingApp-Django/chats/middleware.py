from datetime import datetime
import logging
from django.http import HttpResponse
from django.core.cache import cache
import time

logger = logging.getLogger(__name__)
handler = logging.FileHandler('requests.log')
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        current_hour = datetime.now().hour
        if 9 <= current_hour < 18:  # Allow access only between 9 AM and 6 PM
            response = self.get_response(request)
        else:
            response = HttpResponse(
                "Access restricted to business hours (9 AM - 6 PM).",
                status=403,
                content_type="text/plain"
            )
        return response


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if request.path.startswith('/api/conversations') and request.method == 'POST':
            ip = request.META.get('REMOTE_ADDR')
            cache_key = f"rate-limit:{ip}"
            data = cache.get(cache_key, {"count": 0, "start": time.time()})

            elapsed = time.time() - data["start"]

            if elapsed > self.TIME_WINDOW:
                # reset window
                data = {"count": 1, "start": time.time()}
            else:
                data["count"] += 1

            if data["count"] > self.RATE_LIMIT:
                return HttpResponse("Rate limit exceeded. Try again in a minute.", status=429)

            cache.set(cache_key, data, timeout=self.TIME_WINDOW)

        return None  # continue as usual


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if request.user.role == 'admin' or request.user.role == 'moderator':
            # Allow access to admin users
            return self.get_response(request)
        else:
            # Deny access for other roles
            return HttpResponse("Access denied.", status=403, content_type="text/plain")
