from django.urls import path, reverse_lazy
from .views import *
from .models import *

urlpatterns = [
    path('', CourseList.as_view(), name='course_list'), 
    path('create/', CourseCreate.as_view(), name='course_create'),
    path('<int:cid>/', CourseView.as_view(), name='course_view'), 
    path('<int:cid>/edit/', CourseEdit.as_view(), name='course_edit'),
    path('<int:cid>/enroll/', CourseEnroll.as_view(), name='course_enroll'), 
    path('<int:cid>/users/', CourseUsers.as_view(), name='course_users'),
    path('<int:cid>/seat/', CourseEnrollSeat.as_view(), name='course_seat'),
]
