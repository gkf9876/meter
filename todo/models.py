from django.contrib.auth.models import User
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from tinymce.models import HTMLField


class Todo(MPTTModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    create_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['tree_id', 'lft']

    class MPTTMeta:
        order_insertion_by = ['subject']

    def __str__(self):
        return self.subject

class TodoDetail(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)
    date = models.DateTimeField()
    content = HTMLField()
    use_yn = models.CharField(max_length=2, default='Y')
    create_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)