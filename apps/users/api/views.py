"""User API views."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.core.permissions import IsAuthenticated, IsAdmin, IsAccountActive, OrganizationNotSuspended
from apps.core.pagination import StandardResultsPagination
from apps.users.selectors import get_user_by_id, list_users
from apps.users.services import (
    create_user, update_user, deactivate_user,
    delete_user, change_password, unlock_user, suspend_user,
)
from apps.users.api.serializers import (
    UserPublicSerializer, UserDetailSerializer,
    UserUpdateSerializer, UserCreateSerializer, ChangePasswordSerializer,
)
from apps.roles.selectors import get_role_by_id


class UserListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive, OrganizationNotSuspended]

    @extend_schema(responses=UserPublicSerializer(many=True))
    def get(self, request):
        """List users. Scope depends on requester's role."""
        users = list_users(
            organization=request.organization,
            search=request.query_params.get("search"),
            is_active=request.query_params.get("is_active"),
            requesting_user=request.user,
        )
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(users, request)
        serializer = UserPublicSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=UserCreateSerializer, responses=UserDetailSerializer)
    def post(self, request):
        """Create a user. Requires ADMIN role minimum."""
        if not request.user.get_effective_role_level(request.organization) <= 30:
            from apps.core.exceptions import InsufficientRole
            raise InsufficientRole()

        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        role = get_role_by_id(data["role_id"])
        user = create_user(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password=data.get("password"),
            phone=data.get("phone", ""),
            created_by=request.user,
            organization=request.organization,
            role=role,
            send_verification=True,
            is_email_verified=False,
        )
        return Response(UserDetailSerializer(user, context={"request": request}).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive, OrganizationNotSuspended]

    def _get_user(self, request, user_id):
        """Get user and check access."""
        from apps.core.exceptions import PermissionDeniedException
        user = get_user_by_id(user_id)
        # Users can view themselves; admins can view anyone in their org
        if str(user.id) != str(request.user.id):
            if request.user.get_effective_role_level(request.organization) > 30:
                raise PermissionDeniedException()
        return user

    def get(self, request, user_id):
        user = self._get_user(request, user_id)
        return Response(UserDetailSerializer(user, context={"request": request}).data)

    def patch(self, request, user_id):
        user = self._get_user(request, user_id)
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = update_user(user=user, updated_by=request.user, **serializer.validated_data)
        return Response(UserDetailSerializer(user, context={"request": request}).data)

    def delete(self, request, user_id):
        user = self._get_user(request, user_id)
        delete_user(user=user, deleted_by=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """Current user's own profile."""
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request):
        return Response(UserDetailSerializer(request.user, context={"request": request}).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = update_user(user=request.user, **serializer.validated_data)
        return Response(UserDetailSerializer(user, context={"request": request}).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        change_password(
            user=request.user,
            old_password=data["old_password"],
            new_password=data["new_password"],
        )
        return Response({"message": "Password changed successfully."})


class UnlockUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsAccountActive]

    def post(self, request, user_id):
        user = get_user_by_id(user_id)
        unlock_user(user=user, unlocked_by=request.user)
        return Response({"message": f"User {user.email} has been unlocked."})


class SuspendUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsAccountActive]

    def post(self, request, user_id):
        user = get_user_by_id(user_id)
        suspend_user(user=user, suspended_by=request.user)
        return Response({"message": f"User {user.email} has been suspended."})
