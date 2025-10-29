from django.contrib.auth.models import User
from django.db import models
from tinymce.models import HTMLField

from common.models import File

# Create your models here.

class Info(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = HTMLField()
    create_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)
    use_yn = models.CharField(max_length=2, default='Y')