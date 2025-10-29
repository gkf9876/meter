from django.contrib.auth.models import User
from django.db import models
from tinymce.models import HTMLField

from common.models import File

class Memorization(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    create_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)
    media_file = models.ManyToManyField(File, related_name='media_file_memorization')