# Generated by Django 5.0 on 2023-12-27 07:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meter', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studylist',
            old_name='study_nm',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='studylist',
            old_name='study_type',
            new_name='type',
        ),
    ]