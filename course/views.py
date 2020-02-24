from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.views.generic import *
from django.contrib.auth.mixins import *
from django.contrib import messages
from django import forms
from .models import *
from user.models import Message

class TeacherReqiuredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser and \
            not request.user.groups.filter(name='teacher').exists():
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

COURSE_PERM_GUEST = 0       # 僅非課程人員
COURSE_PERM_STUDENT = 1     # 是修課學生
COURSE_PERM_TEACHER = 2     # 是授課教師
COURSE_PERM_MEMBER = 3      # 是修課學生或授課教師

class CourseAccessMixin(AccessMixin):
    permission = None       # 預設不檢查權限
    extra_context = {}
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        self.course = get_object_or_404(Course, id=kwargs['cid'])

        user_perm = COURSE_PERM_GUEST
        if self.course.teacher == request.user:
            user_perm = COURSE_PERM_TEACHER
        elif self.course.enroll_set.filter(stu=request.user).exists():
            user_perm = COURSE_PERM_STUDENT
        
        if not request.user.is_superuser and self.permission is not None:
            is_accessible = False
            if self.permission == COURSE_PERM_GUEST and \
                user_perm == COURSE_PERM_GUEST:
                is_accessible = True
            elif (self.permission & user_perm) != 0:
                is_accessible = True

            if not is_accessible:
                return self.handle_no_permission()  

        self.extra_context.update({'course': self.course})
        return super().dispatch(request, *args, **kwargs)

class CourseList(ListView): # 課程列表
    extra_context = {'title': '課程列表'}
    model = Course
    ordering = ['-id']
    paginate_by = 20

class CourseCreate(TeacherReqiuredMixin, CreateView):    # 建立課程
    extra_context = {'title': '建立課程'}
    model = Course
    fields = ['name', 'enroll_password']
    template_name = 'form.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

class CourseView(CourseAccessMixin, DetailView):    # 檢視課程
    extra_context = {'title': '檢視課程'}
    model = Course
    pk_url_kwarg = 'cid'

class CourseEdit(CourseAccessMixin, UpdateView):    # 修改課程
    permission = COURSE_PERM_TEACHER
    extra_context = {'title': '修改課程'}
    pk_url_kwarg = 'cid'
    model = Course
    fields = ['name', 'enroll_password']
    template_name = 'form.html'

    def get_success_url(self):
        return reverse('course_view', args=[self.object.id])

class CourseEnroll(CourseAccessMixin, CreateView):  # 選修課程
    permission = COURSE_PERM_GUEST
    model = Enroll
    fields = ['seat']
    template_name = 'form.html'

    def get_success_url(self):
        return reverse('course_view', args=[self.course.id])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = '選修課程：' + self.course.name
        return ctx
    
    def get_form(self):
        form = super().get_form()
        form.fields['password'] = forms.CharField(label='選課密碼', max_length=32)
        return form
    
    def form_valid(self, form):
        if form.cleaned_data['password'] != self.course.enroll_password:
            form.add_error('password', '選課密碼錯誤')
            return super().form_invalid(form)
        form.instance.course = self.course
        form.instance.stu = self.request.user
        return super().form_valid(form)

class CourseUsers(CourseAccessMixin, ListView): # 修課名單
    permission = COURSE_PERM_MEMBER
    extra_context = {'title': '修課名單'}
    template_name = 'course/user_list.html'

    def get_queryset(self):
        return self.course.enroll_set.select_related('stu').order_by('seat')

class CourseEnrollSeat(CourseAccessMixin, UpdateView):  # 變更座號
    permission = COURSE_PERM_STUDENT
    extra_context = {'title': '變更座號'}
    fields = ['seat']
    template_name = 'form.html'

    def get_success_url(self):
        return reverse('course_view', args=[self.course.id])

    def get_object(self):
        return get_object_or_404(
            Enroll,
            course=self.course,
            stu=self.request.user
        )


class MsgList(CourseAccessMixin, ListView):  # 公告列表
    permission = COURSE_PERM_MEMBER
    extra_context = {'title': '公告列表'}
    model = Message
    paginate_by = 20
    template_name = 'course/message_list.html'

    def get_queryset(self):
        self.extra_context.update({
            'read_list': self.request.user.read_list.values_list('message', flat=True)
        })
        return self.course.notices.order_by('-created')

class MsgCreate(CourseAccessMixin, CreateView):  # 教師新增課程公告
    permission = COURSE_PERM_TEACHER
    extra_context = {'title': '新增公告'}
    model = Message
    fields = ['title', 'body']
    template_name = 'user/message_form.html'

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, '公告已張貼！')
        return self.request.POST.get('success_url')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['success_url'] = self.request.META.get('HTTP_REFERER', '/')
        ctx['course'] = self.course
        return ctx

    def form_valid(self, form):
        form.instance.course = self.course
        form.instance.sender = self.request.user
        return super().form_valid(form)
