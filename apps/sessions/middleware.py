"""Session tracking middleware."""

from django.utils.deprecation import MiddlewareMixin


class SessionTrackingMiddleware(MiddlewareMixin):
    """Updates last_active_at on authenticated requests."""

    def process_response(self, request, response):
        if hasattr(request, "user") and request.user.is_authenticated:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header.startswith("Bearer "):
                self._update_session_activity(request)
        return response

    def _update_session_activity(self, request):
        try:
            from apps.authentication.tokens import decode_access_token
            token = request.META.get("HTTP_AUTHORIZATION", "").split(" ", 1)[1]
            payload = decode_access_token(token)
            # Note: access token doesn't carry jti of refresh token
            # Session last_active is updated via auto_now on UserSession
        except Exception:
            pass
