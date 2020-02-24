from django.db.models import *
from django.contrib.auth.models import User
from course.models import Course, Enroll


class Message(Model):
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


class MessageStatus(Model):
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
