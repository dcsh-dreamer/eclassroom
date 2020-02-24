from django.urls import path, include
from .views import *
from .models import *

msg_urlpatterns = ([
    path('', MsgList.as_view(), name='course_msglist'),
    path('broadcast/', MsgCreate.as_view(), name='course_msgbroadcast'),
])

urlpatterns = [
    path('', CourseList.as_view(), name='course_list'), 
    path('create/', CourseCreate.as_view(), name='course_create'),
    path('<int:cid>/', CourseView.as_view(), name='course_view'), 
    path('<int:cid>/edit/', CourseEdit.as_view(), name='course_edit'),
    path('<int:cid>/enroll/', CourseEnroll.as_view(), name='course_enroll'), 
    path('<int:cid>/users/', CourseUsers.as_view(), name='course_users'),
    path('<int:cid>/seat/', CourseEnrollSeat.as_view(), name='course_seat'),
    path('<int:cid>/msg/', include(msg_urlpatterns)),
]
