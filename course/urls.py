from django.urls import path, include
from .views import *

msg_urlpatterns = [
    path('', MsgList.as_view(), name='course_msglist'),
    path('broadcast/', MsgCreate.as_view(), name='course_msgbroadcast'),
]

assignment_urls = [
    path('', AssignmentList.as_view(), name='assignment_list'), 
    path('create/', AssignmentCreate.as_view(), name='assignment_create'),
    path('<int:aid>/', AssignmentView.as_view(), name='assignment_view'),
    path('<int:aid>/submit/', WorkSubmit.as_view(), name='work_submit'),
    path('work/<int:wid>/', WorkUpdate.as_view(), name='work_update'),
    path('score/<int:wid>/', WorkScore.as_view(), name='work_score'),
]

urlpatterns = [
    path('', CourseList.as_view(), name='course_list'), 
    path('create/', CourseCreate.as_view(), name='course_create'),
    path('<int:cid>/', CourseView.as_view(), name='course_view'), 
    path('<int:cid>/edit/', CourseEdit.as_view(), name='course_edit'),
    path('<int:cid>/enroll/', CourseEnroll.as_view(), name='course_enroll'), 
    path('<int:cid>/users/', CourseUsers.as_view(), name='course_users'),
    path('<int:cid>/seat/', CourseEnrollSeat.as_view(), name='course_seat'),
    path('<int:cid>/msg/', include(msg_urlpatterns)),
    path('<int:cid>/assign/', include(assignment_urls)),
]
