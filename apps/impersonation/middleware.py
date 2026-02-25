"""Impersonation context middleware."""

from django.utils.deprecation import MiddlewareMixin


class ImpersonationMiddleware(MiddlewareMixin):
    """
    Detects impersonation token in request headers.
    Sets request.impersonating = True and request.real_user = <actual user>
    """

    def process_request(self, request):
        request.impersonating = False
        request.real_user = None

        imp_token = request.META.get("HTTP_X_IMPERSONATION_TOKEN")
        if imp_token and hasattr(request, "user") and request.user.is_authenticated:
            self._resolve_impersonation(request, imp_token)

    def _resolve_impersonation(self, request, token):
        try:
            from apps.impersonation.models import ImpersonationSession
            session = ImpersonationSession.objects.select_related("target", "impersonator").get(
                impersonation_token=token,
                impersonator=request.user,
                is_active=True,
            )
            request.real_user = request.user
            request.user = session.target
            request.impersonating = True
        except Exception:
            pass
