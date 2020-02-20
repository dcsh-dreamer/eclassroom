from django import template
from django.contrib.auth.models import User, Group

register = template.Library()

@register.filter(name='in_group')
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter(name='is_teacher')
def is_teacher(user):
    return user.groups.filter(name='teacher').exists()