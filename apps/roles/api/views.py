"""Role API views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.permissions import IsAuthenticated, IsAdmin, IsAccountActive
from apps.roles.selectors import list_roles, get_role_by_id
from apps.roles.hierarchy import get_assignable_roles, validate_role_change
from apps.roles.services import assign_role_to_user
from apps.core.exceptions import InsufficientRole


class RoleListView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request):
        """List roles assignable by this user."""
        roles = get_assignable_roles(request.user, request.organization)
        return Response([{"id": str(r.id), "name": r.name, "level": r.level} for r in roles])


class AssignRoleView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsAccountActive]

    def post(self, request):
        user_id = request.data.get("user_id")
        role_id = request.data.get("role_id")
        if not user_id or not role_id:
            from apps.core.exceptions import ValidationError
            raise ValidationError("user_id and role_id are required.")
        from apps.users.selectors import get_user_by_id
        user = get_user_by_id(user_id)
        role = get_role_by_id(role_id)
        assign_role_to_user(assigner=request.user, user=user, role=role, organization=request.organization)
        return Response({"message": f"Role {role.name} assigned to {user.email}."})
