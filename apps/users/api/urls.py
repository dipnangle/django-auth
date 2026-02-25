from django.urls import path
from apps.users.api.views import (
    UserListCreateView, UserDetailView,
    MeView, ChangePasswordView, UnlockUserView, SuspendUserView,
)

app_name = "users"

urlpatterns = [
    path("", UserListCreateView.as_view(), name="user-list-create"),
    path("me/", MeView.as_view(), name="me"),
    path("me/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("<uuid:user_id>/", UserDetailView.as_view(), name="user-detail"),
    path("<uuid:user_id>/unlock/", UnlockUserView.as_view(), name="user-unlock"),
    path("<uuid:user_id>/suspend/", SuspendUserView.as_view(), name="user-suspend"),
]
