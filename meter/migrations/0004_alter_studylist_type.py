# Generated by Django 5.0 on 2023-12-27 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meter', '0003_alter_study_memo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studylist',
            name='type',
            field=models.CharField(max_length=200),
        ),
    ]