"""Permissions API views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.permissions import IsAuthenticated, IsAdmin, IsAccountActive
from apps.permissions.selectors import get_all_user_features
from apps.permissions.constants import Feature


class FeatureListView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request):
        features = get_all_user_features(request.user, request.organization)
        return Response(features)


class PermissionOverrideView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsAccountActive]

    def post(self, request):
        from apps.permissions.models import UserPermissionOverride
        from apps.users.selectors import get_user_by_id
        user = get_user_by_id(request.data.get("user_id"))
        feature = request.data.get("feature")
        is_granted = request.data.get("is_granted", True)
        override, _ = UserPermissionOverride.objects.update_or_create(
            user=user, feature=feature,
            defaults={"is_granted": is_granted, "granted_by": request.user},
        )
        return Response({"feature": feature, "is_granted": is_granted})
