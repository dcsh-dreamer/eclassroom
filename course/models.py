from django.db.models import *
from django.contrib.auth.models import User

# 課程
class Course(Model):
    name = CharField('課程名稱', max_length=32)
    enroll_password = CharField('選課密碼', max_length=32)
    teacher = ForeignKey(User, CASCADE)     # 開課教師

    def __str__(self):
        return "{}: {}({})".format(
            self.id,
            self.name, 
            self.teacher.first_name
        )

# 選課
class Enroll(Model):
    stu = ForeignKey(User, CASCADE)         # 選修學生
    course = ForeignKey(Course, CASCADE)    # 選修課程
    seat = IntegerField('座號', default=0)

    def __str__(self):
        return "{}: {}-{}-{}".format(
            self.id, 
            self.course.name, 
            self.seat, 
            self.stu.first_name
        )

# 作業
class Assignment(Model):
    title = CharField('作業名稱', max_length=255)
    desc = TextField('作業說明', null=True, default=None)
    course = ForeignKey(Course, CASCADE, related_name='assignments')
    created = DateTimeField('建立時間', auto_now_add=True)

    def __str__(self):
        return "{}:{}:{}".format(
            self.id, 
            self.course.name, 
            self.title
        )

# 作品
class Work(Model):
    assignment = ForeignKey(Assignment, CASCADE, related_name='works')
    user = ForeignKey(User, CASCADE, related_name='works')
    memo = TextField('心得', blank=True, default='')
    attachment = FileField('附件', upload_to='work/', null=True)
    created = DateTimeField(auto_now_add=True)
    score = IntegerField('成績', default=0)

    def __str__(self):
        return "{}:({}){}-{}".format(
            self.id, 
            self.assignment.course.name, 
            self.assignment.title,
            self.user.first_name, 
        )