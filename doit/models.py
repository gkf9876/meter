from django.contrib.auth.models import User
from django.db import models
from tinymce.models import HTMLField

from common.models import File


class Doit(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    notice_yn = models.BooleanField(default=False)
    create_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)
    file = models.ManyToManyField(File, related_name='file_doit')
    voter = models.ManyToManyField(User, related_name='voter_doit')
    viewcount = models.ManyToManyField(User, related_name='viewcount_doit')

class DoitDetail(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    doit = models.ForeignKey(Doit, on_delete=models.CASCADE)
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    create_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_doitdetail')