from django.urls import path
from .views import (
    AdminUserList,
    AdminUserDetail,
    AdminToggleBlockUser,
    AdminDeleteUser,
    DashboardStatsView,
    AdminReportsView,
)

urlpatterns = [
    path("users/", AdminUserList.as_view()),
    path("users/<int:id>/", AdminUserDetail.as_view()),
    path("users/<int:id>/toggle-block/", AdminToggleBlockUser.as_view()),
    path("users/<int:id>/delete/", AdminDeleteUser.as_view()),

    path("dashboard/", DashboardStatsView.as_view()),
    path("reports/", AdminReportsView.as_view()),
]
