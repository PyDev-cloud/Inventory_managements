from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, DashboardView,
    ManageUsersView, ChangeRoleView, ManagePermissionsView,
)

app_name = 'user'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('manage-users/', ManageUsersView.as_view(), name='manage_users'),
    path('change-role/<int:user_id>/', ChangeRoleView.as_view(), name='change_role'),
    path('manage-permissions/', ManagePermissionsView.as_view(), name='manage_permissions'),
]