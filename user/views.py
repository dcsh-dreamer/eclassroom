from django.views.generic import *
from django.urls import reverse_lazy
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q, Subquery, OuterRef
from django import forms
from django.contrib import messages
from .models import *

# 限定管理員才允許操作的混成類別
class SuperuserRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

# 使用者註冊
class UserRegister(CreateView):
    extra_context = {'title': '使用者註冊'}
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'password']
    template_name = 'form.html'
    success_url = reverse_lazy('home')  # 註冊完成返回首頁

    # 
    def get_form(self):
        form = super().get_form()
        form.fields['first_name'].label = '真實姓名'
        form.fields['first_name'].required = True
        form.fields['last_name'].label = '學校名稱'
        form.fields['last_name'].required = True
        form.fields['password2'] = forms.CharField(label='密碼驗證', max_length=255)
        return form

    # 表單驗證
    def form_valid(self, form):
        user = form.save(commit=False)
        pw1 = form.cleaned_data['password']
        pw2 = form.cleaned_data['password2']
        if pw1 != pw2:
            form.add_error('password2', '密碼與驗證密碼不相符')
            return super().form_invalid(form)
        user.set_password(pw1)
        return super().form_valid(form)

# 使用者列表
class UserList(SuperuserRequiredMixin, ListView):
    extra_context = {'title': '使用者列表'}
    model = User
    ordering = ['username']
    paginate_by = 20
    template_name = 'user/user_list.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('groups')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_list = []
        for user in self.object_list:
            is_teacher = user.groups.filter(name='teacher').exists()
            user_list.append((user, is_teacher))
        ctx['ulist'] = user_list
        return ctx

class UserView(SuperuserRequiredMixin, DetailView):
    model = User
    template_name = 'user/user_detail.html'
    context_object_name = 'tuser'

class UserEdit(SuperuserRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email']
    success_url = reverse_lazy('user_list')
    template_name = 'form.html'

    def get_form(self):
        form = super().get_form()
        form.fields['first_name'].label = '真實姓名'
        form.fields['first_name'].required = True
        form.fields['last_name'].label = '學校名稱'
        form.fields['last_name'].required = True
        return form

class UserPasswordUpdate(SuperuserRequiredMixin, UpdateView):
    model = User
    fields = ['password']
    success_url = reverse_lazy('user_list')
    template_name = 'form.html'

    def get_form(self):
        form = super().get_form()
        form.fields['password2'] = forms.CharField(label='密碼驗證', max_length=255)
        return form
    
    def get_initial(self):  # 指定初始值來清掉密碼輸入欄位的原始值
        return {'password': ''}
    
    def form_valid(self, form):
        user = form.save(commit=False)
        pw1 = form.cleaned_data['password']
        pw2 = form.cleaned_data['password2']
        if pw1 != pw2:
            form.add_error('password2', '密碼與驗證密碼不相符')
            return super().form_invalid(form)
        user.set_password(pw1)
        return super().form_valid(form)

class UserTeacherToggle(SuperuserRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user = User.objects.get(id=self.kwargs['uid'])
        try :
            group = Group.objects.get(name="teacher")	
        except ObjectDoesNotExist :
            group = Group(name="teacher")
            group.save()

        if user.groups.filter(name='teacher').exists():
            group.user_set.remove(user)
        else: 
            group.user_set.add(user)
        return self.request.META.get('HTTP_REFERER', '/')

class UserDashboard(LoginRequiredMixin, TemplateView):
    extra_context = {'title': '我的儀表板'}
    template_name = 'user/user_detail.html'
    context_object_name = 'tuser'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tuser'] = self.request.user
        return ctx

class MsgList(LoginRequiredMixin, ListView):
    extra_context = {'title': '收件匣'}
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        return Message.objects.annotate(
            read=Subquery(user.read_list.filter(
                message=OuterRef('pk')).values('read'))
        ).filter(
            Q(recipient=user) | Q(course__in=user.enroll_set.values('course'))
        ).select_related('course', 'sender').order_by('-created')

class MsgOutbox(LoginRequiredMixin, ListView):
    extra_context = {'title': '寄件匣'}

    def get_queryset(self):
        user = self.request.user
        return user.outbox.annotate(
            read=Subquery(user.read_list.filter(
                message=OuterRef('pk')).values('id'))
        ).select_related('course', 'recipient').order_by('-created')

class MsgRead(LoginRequiredMixin, DetailView):
    model = Message
    pk_url_kwarg = 'mid'

    def get_queryset(self):
        return super().get_queryset().select_related('course', 'sender')

    def get_context_data(self, **kwargs):
        user = self.request.user
        msg = self.object
        if not msg.status.filter(user=user).exists():
            MessageStatus(message=msg, user=user).save()
        return super().get_context_data()

class MsgSend(LoginRequiredMixin, CreateView):
    extra_context = {'title': '傳送訊息'}
    fields = ['title', 'body']
    model = Message

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['recipient'] = User.objects.get(id=self.kwargs['rid'])
        ctx['success_url'] = self.request.META.get('HTTP_REFERER', '/')
        return ctx

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.recipient = User.objects.get(id=self.kwargs['rid'])
        return super().form_valid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, '訊息已送出！')
        return self.request.POST.get('success_url')

class MsgReply(LoginRequiredMixin, CreateView):
    extra_context = {'title': '回覆訊息'}
    model = Message
    fields = ['title', 'body']

    def get_initial(self):
        self.msg = Message.objects.get(id=self.kwargs['mid'])
        return {
            'title': 'Re: '+self.msg.title,
            'body':  "{}({}) 於 {} 寫道：\n> {}".format(
                self.msg.sender.username,
                self.msg.sender.first_name,
                self.msg.created,
                "\n> ".join(self.msg.body.split('\n'))
            ),
        }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['recipient'] = self.msg.sender
        ctx['success_url'] = self.request.META.get('HTTP_REFERER', '/')
        return ctx

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.recipient = self.msg.sender
        return super().form_valid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, '訊息已送出！')
        return self.request.POST.get('success_url')
