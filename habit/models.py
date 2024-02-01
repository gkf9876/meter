from django.contrib.auth.models import User
from django.db import models
from tinymce.models import HTMLField

class Habit(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    notice_yn = models.BooleanField(default=False)
    create_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)

class HabitDetail(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    create_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)