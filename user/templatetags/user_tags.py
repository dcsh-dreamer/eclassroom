from django import template

register = template.Library()

@register.filter(name='is_teacher')
def is_teacher(user):
    return user.groups.filter(name='teacher').exists()

@register.filter(name='has_student')
def has_student(course, user):
    return course.enroll_set.filter(stu=user).exists()

@register.filter(name='has_member')
def has_member(course, user):
    return course.teacher == user or \
        course.enroll_set.filter(stu=user).exists()