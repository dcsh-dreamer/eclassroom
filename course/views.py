from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.views.generic import *
from django.contrib.auth.mixins import *
from django.contrib import messages
from django import forms
from .models import *
from django.db.models import Subquery, OuterRef
from user.models import Message, PointHistory

class TeacherReqiuredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser and \
            not request.user.groups.filter(name='teacher').exists():
            return super().handle_no_permission()

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

class CourseUsers(CourseAccessMixin, ListView):  # 修課名單
    permission = COURSE_PERM_MEMBER
    extra_context = {'title': '修課名單'}
    template_name = 'course/user_list.html'

    def get_queryset(self):
        return self.course.enroll_set.select_related('stu')\
            .annotate(
                points = Sum('stu__point_list__point')
            ).order_by('seat')

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
        return self.course.notices.annotate(
            read=Subquery(self.request.user.read_list.filter(
                message=OuterRef('id')).values('read'))
        ).order_by('-created')

class MsgCreate(CourseAccessMixin, CreateView):  # 教師新增課程公告
    permission = COURSE_PERM_TEACHER
    extra_context = {'title': '新增公告'}
    model = Message
    fields = ['title', 'body']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['success_url'] = self.request.META.get('HTTP_REFERER', '/')
        return ctx

    def form_valid(self, form):
        form.instance.course = self.course
        form.instance.sender = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, '公告已張貼！')
        return self.request.POST.get('success_url')

class AssignmentList(CourseAccessMixin, ListView):
    extra_context = {'title': '作業列表'}
    permission = COURSE_PERM_MEMBER
    paginate_by = 15

    def get_queryset(self):
        return self.course.assignments.annotate(
            submitted=Subquery(
                self.request.user.works.filter(
                    assignment=OuterRef('id')
                ).values('created')
            )
        ).order_by('-created')

class AssignmentCreate(CourseAccessMixin, CreateView):
    extra_context = {'title': '新增作業'}
    permission = COURSE_PERM_TEACHER
    model = Assignment
    fields = ['title', 'desc']

    def form_valid(self, form):
        form.instance.course = self.course
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('assignment_list', args=[self.course.id])

class AssignmentEdit(CourseAccessMixin, UpdateView):
    extra_context = {'title': '修改作業'}
    permission = COURSE_PERM_TEACHER
    model = Assignment
    fields = ['title', 'desc']
    pk_url_kwarg = 'aid'

    def get_success_url(self):
        return reverse('assignment_view', args=[self.course.id, self.object.id])

class AssignmentView(CourseAccessMixin, DetailView):
    extra_context = {'title': '檢視作業'}
    permission = COURSE_PERM_MEMBER
    model = Assignment
    pk_url_kwarg = 'aid'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_superuser or self.course.teacher == self.request.user:
            sq = self.object.works.filter(user=OuterRef('stu'))
            ctx['work_list'] = self.course.enroll_set.annotate(
                wid = Subquery(sq.values('id')), 
                submitted = Subquery(sq.values('created')),
                score = Subquery(sq.values('score')),
            ).order_by('seat').values('seat', 'stu__first_name', 'wid', 'submitted', 'score')
        else:
            mywork = self.object.works.filter(user=self.request.user).order_by('-id')
            if mywork:
                ctx['mywork'] = mywork[0]
        return ctx

class WorkSubmit(CourseAccessMixin, CreateView):
    extra_context = {'title': '繳交作業'}
    permission = COURSE_PERM_STUDENT
    model = Work
    fields = ['memo', 'attachment']
    template_name = 'form.html'

    def form_valid(self, form):
        form.instance.assignment = Assignment(id=self.kwargs['aid'])
        form.instance.user = self.request.user
        # 繳交作業累積 2 點積分
        PointHistory(
            user = form.instance.user,
            assignment = form.instance.assignment, 
            reason = '繳交作業', 
            point = 2
        ).save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse(
            'assignment_view', 
            args=[self.course.id, self.object.assignment.id]
        )

class WorkUpdate(UpdateView):
    extra_context = {'title': '修改作業'}
    model = Work
    fields = ['memo', 'attachment']
    template_name = 'form.html'
    pk_url_kwarg = 'wid'

    def get_object(self):
        work = super().get_object()
        if not work.user == self.request.user:
            raise PermissionDenied("欲修改的作業不是你做的，不允許改修")
        if work.score > 0:
            raise PermissionDenied("作業已完成評分，不允許修改")
        return work

    def get_success_url(self):
        return reverse(
            'assignment_view', 
            args=[self.course.id, self.object.assignment.id]
        )

class WorkScore(CourseAccessMixin, UpdateView):
    extra_context = {'title': '批改作業'}
    permission = COURSE_PERM_TEACHER
    model = Work
    fields = ['score']
    pk_url_kwarg = 'wid'

    def get_success_url(self):
        return reverse(
            'assignment_view', 
            args=[self.course.id, self.object.assignment.id]
        )
    
    def get_form(self):
        form = super().get_form()
        form.fields['score'] = forms.ChoiceField(
            label = '成績', 
            choices = [
                (100, "你好棒(100分)"), 
                (90, "90分"),
                (80, "80分"),
                (70, "70分"),
                (60, "60分"),
            ],
        )
        self.oldscore = self.object.score # 本次評分前原始成績
        return form
    
    def form_valid(self, form):
        def score_to_point(score): # 成績轉換為點數
            return 2 if score >= 90 else 1 if score >= 80 else 0

        oscore = self.oldscore          # 原始成績
        nscore = form.instance.score    # 本次成績
        opoint = score_to_point(oscore) # 原始成績積點
        npoint = score_to_point(nscore) # 本次成績積點

        if opoint != npoint:
            PointHistory(
                user = self.object.user, 
                assignment = self.object.assignment, 
                reason = f'教師評分: {oscore} -> {nscore}',
                point = npoint - opoint,
            ).save()
        return super().form_valid(form)
