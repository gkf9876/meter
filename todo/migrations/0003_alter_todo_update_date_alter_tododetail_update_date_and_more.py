# Generated by Django 5.0 on 2023-12-28 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_alter_todo_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='update_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='tododetail',
            name='update_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='tododetail',
            name='use_yn',
            field=models.CharField(default='Y', max_length=2),
        ),
    ]
