from django.db.models import *
from django.contrib.auth.models import User
from course.models import Course, Assignment

class Message(Model):   # 訊息
    sender = ForeignKey(User, CASCADE, related_name='outbox')
    course = ForeignKey(
        Course, CASCADE, related_name='notices', null=True, default=None)
    recipient = ForeignKey(
        User, CASCADE, related_name='inbox', null=True, default=None)
    title = CharField('主旨', max_length=255)
    body = TextField('內容')
    created = DateTimeField('時間', auto_now_add=True)

    def __str__(self):
        return "{}: {}-{}".format(
            self.id,
            self.sender,
            self.title
        )

class MessageStatus(Model): # 訊息讀取紀錄
    message = ForeignKey(Message, CASCADE, related_name='status')
    user = ForeignKey(User, CASCADE, related_name='read_list')
    read = DateTimeField('閱讀時間', auto_now_add=True)

    def __str__(self):
        return "{}: {}-{} @{}".format(
            self.id,
            self.message.sender,
            self.message.title,
            self.read
        )

class PointHistory(Model): # 使用者積點紀錄
    user = ForeignKey(User, CASCADE, related_name='point_list')
    assignment = ForeignKey(Assignment, CASCADE, related_name='+')
    reason = CharField('積點原因', max_length=100)
    point = IntegerField('點數', default=0)
    created = DateTimeField('積點時間', auto_now_add=True)

    def __str__(self):
        return "{}: {} {}點".format(
            self.created, 
            self.reason, 
            self.point
        )

class Questionnaire(Model):   # 問卷
    ACCEPTANCE_CHOICES = [
        (1, '非常不同意'), 
        (2, '不同意'),
        (3, '同意'),
        (4, '非常同意'),
    ]
    user = ForeignKey(User, CASCADE, related_name='questionary')
    q1 = IntegerField(
        '1.我很崇拜程式設計很厲害的人', default=0, choices=ACCEPTANCE_CHOICES)
    q2 = IntegerField(
        '2.我對學習程式設計感到有興趣', default=0, choices=ACCEPTANCE_CHOICES)
    q3 = IntegerField(
        '3.學好程式設計在現代社會是很重要的', default=0, choices=ACCEPTANCE_CHOICES)
    t1 = TextField('4.請列舉曾經學過的程式語言', default='')
    t2 = TextField('5.請簡述對本課程的期望', default='')
    # created = DateTimeField(auto_now_add=True)
    # updated = DateTimeField(auto_now_add=True, auto_now=True)