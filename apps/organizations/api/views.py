"""Organization API views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.permissions import IsAuthenticated, IsSuperAdmin, IsAccountActive
from apps.organizations.selectors import get_organization_by_id, list_organization_members
from apps.organizations.services import create_organization, remove_member_from_organization


class OrgListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request):
        from apps.organizations.selectors import list_user_organizations
        orgs = list_user_organizations(request.user)
        return Response([{"id": str(o.id), "name": o.name, "slug": o.slug} for o in orgs])

    def post(self, request):
        self.permission_classes = [IsAuthenticated, IsSuperAdmin, IsAccountActive]
        self.check_permissions(request)
        org = create_organization(name=request.data.get("name"), created_by=request.user)
        return Response({"id": str(org.id), "name": org.name, "slug": org.slug}, status=status.HTTP_201_CREATED)


class OrgDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request, org_id):
        org = get_organization_by_id(org_id)
        return Response({"id": str(org.id), "name": org.name, "slug": org.slug, "is_active": org.is_active})


class OrgMembersView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request, org_id):
        org = get_organization_by_id(org_id)
        members = list_organization_members(org)
        return Response([{"user": str(m.user.email), "role": m.role.name} for m in members])

    def delete(self, request, org_id):
        org = get_organization_by_id(org_id)
        user_id = request.data.get("user_id")
        from apps.users.selectors import get_user_by_id
        user = get_user_by_id(user_id)
        remove_member_from_organization(organization=org, user=user, removed_by=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
