# Generated by Django 5.0 on 2024-01-02 23:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meter', '0009_studylist_upload_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studylist',
            name='upload_file',
        ),
    ]
