"""Plans API views — ROOT only."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.permissions import IsRoot, IsAuthenticated, IsAccountActive
from apps.plans.selectors import list_plans, get_active_license
from apps.plans.services import assign_license


class PlanListView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request):
        plans = list_plans()
        return Response([{"id": str(p.id), "name": p.name, "tier": p.tier} for p in plans])


class LicenseAssignView(APIView):
    permission_classes = [IsAuthenticated, IsRoot, IsAccountActive]

    def post(self, request):
        from apps.plans.models import Plan
        from apps.organizations.selectors import get_organization_by_id
        org = get_organization_by_id(request.data.get("organization_id"))
        plan = Plan.objects.get(id=request.data.get("plan_id"))
        license = assign_license(organization=org, plan=plan, created_by=request.user)
        return Response({"id": str(license.id), "plan": plan.name}, status=status.HTTP_201_CREATED)
