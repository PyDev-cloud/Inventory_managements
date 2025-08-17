from userAccount.models import RolePermission

# Central list of permission keys used across the app
PERMISSION_KEYS = [
    'access_dashboard',
    'manage_users',
    'manage_permissions',
    'view_accounts',
    'edit_accounts',
    'view_products',
    'edit_products',
    'create_order',
    'update_order',
    'delete_order',
]

def has_permission(user, permission: str) -> bool:
    """Return True if user has the given permission name."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role = getattr(user, 'user_type', 'Customer')
    try:
        rp = RolePermission.objects.get(role=role, permission=permission)
        return rp.allowed
    except RolePermission.DoesNotExist:
        return False
