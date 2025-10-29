from django.contrib.auth.models import User
from django.db import models
from tinymce.models import HTMLField

from common.models import File

class ScheduleItem(models.Model):
    title = models.CharField(max_length=100)             # 일정 이름
    start_time = models.TimeField()                      # 시작 시각
    end_time = models.TimeField()                        # 종료 시각
    color = models.CharField(max_length=7, default="#90CAF9")  # 색상(hex 코드)
    use_yn = models.CharField(max_length=2, default='Y')
    created_at = models.DateTimeField(auto_now_add=True) # 등록일
    updated_at = models.DateTimeField(auto_now=True)     # 수정일

    def duration_minutes(self):
        """일정의 총 분 단위 길이"""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        return end_minutes - start_minutes

    def __str__(self):
        return f"{self.title} ({self.start_time}~{self.end_time})"

class Schedule(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    notice_yn = models.BooleanField(default=False)
    create_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)
    schedule_item = models.ManyToManyField(ScheduleItem, related_name='item_schedule')
    file = models.ManyToManyField(File, related_name='file_schedule')

class ScheduleDetail(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    create_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)