from django import template
from utils.permissions import has_permission as _has_permission

register = template.Library()

@register.filter
def has_permission(user, permission_name):
    return _has_permission(user, permission_name)
