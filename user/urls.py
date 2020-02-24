from django.urls import path, include
from .views import *

msg_urlpatterns = ([
    path('', MsgList.as_view(), name='user_inbox'), 
    path('outbox/', MsgOutbox.as_view(), name='user_outbox'),
    path('<int:mid>/', MsgRead.as_view(), name='user_msgread'),
    path('<int:mid>/reply/', MsgReply.as_view(), name='user_msgreply'),
    path('send/<int:rid>/', MsgSend.as_view(), name='user_msgsend'), 
])

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', UserDashboard.as_view(), name='user_dashboard'),
    path('list/', UserList.as_view(), name='user_list'),
    path('register/', UserRegister.as_view(), name='user_register'),
    path('<int:pk>/', UserView.as_view(), name='user_view'),
    path('<int:pk>/edit/', UserEdit.as_view(), name='user_edit'),
    path('<int:pk>/password/', UserPasswordUpdate.as_view(), name='user_password'),
    path('<int:uid>/teacher/', UserTeacherToggle.as_view(), name='user_teacher_toggle'),
    path('msg/', include(msg_urlpatterns)),
]