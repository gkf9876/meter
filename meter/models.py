from django.contrib.auth.models import User
from django.db import models


class Study(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    create_date = models.DateTimeField()
    use_yn = models.CharField(max_length=2, default='Y')

    def __str__(self):
        return self.name

class Meter(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    memo = models.TextField()

    def __str__(self):
        diff = self.end_date - self.start_date
        return self.study.name + " (" + str(diff) + ")"
