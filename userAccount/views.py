from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import FormMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from .models import User, USER_TYPES, RolePermission
from .forms import RegisterForm, LoginForm
from .utils.permissions import has_permission, PERMISSION_KEYS


class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class RegisterView(FormView):
    template_name = 'userAccount_Temp/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('user:login')

    def form_valid(self, form):
        User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            user_type='Customer',
        )
        messages.success(self.request, 'Registration successful. Please login.')
        return super().form_valid(form)
    



class LoginView(FormView):
    template_name = 'userAccount_Temp/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)  # ✅ প্রথমে লগইন কর

        # ✅ তারপর user_type অনুযায়ী রিডাইরেকশন
        if user.user_type == 'Customer':
            return redirect('ecommerce:product_list')
        elif user.user_type in ['Manager', 'Accounts', 'Sales_Team', 'Employee']:
            return redirect('dashboard')
        else:
            return redirect('dashboard')
    


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('user:login')
    


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'userAccount_Temp/home.html'

    def dispatch(self, request, *args, **kwargs):
        if not has_permission(request.user, 'access_dashboard') and not request.user.is_superuser:
            return self.render_to_response({})
        return super().dispatch(request, *args, **kwargs)


class ManageUsersView(LoginRequiredMixin, SuperuserRequiredMixin, TemplateView):
    template_name = 'userAccount_Temp/manage_users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.exclude(id=self.request.user.id)
        context['roles'] = [k for k, _ in USER_TYPES if k != 'Superuser']
        return context
    


class ChangeRoleView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        new_role = request.POST.get('role')
        valid_roles = [k for k, _ in USER_TYPES if k != 'Superuser']

        if new_role in valid_roles:
            user.user_type = new_role
            user.is_staff = (new_role != 'Customer')
            user.save()
            messages.success(request, f'Role updated for {user.username} -> {new_role}')
        else:
            messages.error(request, 'Invalid role')

        return redirect('user:manage_users')




class ManagePermissionsView(LoginRequiredMixin, SuperuserRequiredMixin, TemplateView):
    template_name = 'userAccount_Temp/manage_permissions.html'

    def get(self, request, *args, **kwargs):
        self.role = self.get_role()
        self.ensure_role_permissions()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.role = self.get_role()
        permissions = RolePermission.objects.filter(role=self.role)
        checked = set(request.POST.getlist('permissions'))

        for rp in permissions:
            rp.allowed = rp.permission in checked
            rp.save()

        messages.success(request, f'Permissions updated for role: {self.role}')
        return redirect(f"{request.path}?role={self.role}")

    def get_role(self):
        roles = [k for k, _ in USER_TYPES if k != 'Superuser']
        return self.request.GET.get('role') or (roles[0] if roles else 'Customer')

    def ensure_role_permissions(self):
        for key in PERMISSION_KEYS:
            RolePermission.objects.get_or_create(role=self.role, permission=key, defaults={'allowed': False})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        roles = [k for k, _ in USER_TYPES if k != 'Superuser']
        context['roles'] = roles
        context['active_role'] = self.role
        context['permissions'] = RolePermission.objects.filter(role=self.role).order_by('permission')
        return context
