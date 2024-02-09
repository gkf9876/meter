# Generated by Django 5.0 on 2024-02-09 10:48

import django.db.models.deletion
import tinymce.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Habit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('content', tinymce.models.HTMLField()),
                ('use_yn', models.CharField(default='Y', max_length=2)),
                ('notice_yn', models.BooleanField(default=False)),
                ('create_date', models.DateTimeField()),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('file', models.ManyToManyField(related_name='file_habit', to='common.file')),
            ],
        ),
        migrations.CreateModel(
            name='HabitDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', tinymce.models.HTMLField()),
                ('use_yn', models.CharField(default='Y', max_length=2)),
                ('create_date', models.DateTimeField()),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('habit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='habit.habit')),
            ],
        ),
    ]
