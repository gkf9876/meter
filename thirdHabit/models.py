from django.contrib.auth.models import User
from django.db import models
from tinymce.models import HTMLField

from common.models import File


class ThirdHabitItemDetailTime(models.Model):
    DAY_CHOICES = [
        ('MON', '월'),
        ('TUE', '화'),
        ('WED', '수'),
        ('THU', '목'),
        ('FRI', '금'),
        ('SAT', '토'),
        ('SUN', '일'),
    ]
    start_day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()                      # 시작 시각
    end_day = models.CharField(max_length=3, choices=DAY_CHOICES)
    end_time = models.TimeField()                        # 종료 시각
    use_yn = models.CharField(max_length=2, default='Y')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(null=True, blank=True)

class ThirdHabitItemDetail(models.Model):
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(null=True, blank=True)
    detailTimeItem = models.ManyToManyField(ThirdHabitItemDetailTime, related_name='detailTimeItem_thirdHabit')

class ThirdHabitItem(models.Model):
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(null=True, blank=True)
    detailItem = models.ManyToManyField(ThirdHabitItemDetail, related_name='detailItem_thirdHabit')

class ThirdHabit(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    notice_yn = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(null=True, blank=True)
    item = models.ManyToManyField(ThirdHabitItem, related_name='item_thirdHabit')
    file = models.ManyToManyField(File, related_name='file_thirdHabit')
    voter = models.ManyToManyField(User, related_name='voter_thirdHabit')
    viewcount = models.ManyToManyField(User, related_name='viewcount_thirdHabit')

class ThirdHabitDetail(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    thirdHabit = models.ForeignKey(ThirdHabit, on_delete=models.CASCADE)
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(null=True, blank=True)