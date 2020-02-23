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
