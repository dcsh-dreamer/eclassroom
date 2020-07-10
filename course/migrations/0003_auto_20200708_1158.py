# Generated by Django 2.2.14 on 2020-07-08 03:58

import course.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_assignment_work'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='course.Course'),
        ),
        migrations.AlterField(
            model_name='work',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='works', to='course.Assignment'),
        ),
        migrations.AlterField(
            model_name='work',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to=course.models.work_attach, verbose_name='附件'),
        ),
        migrations.AlterField(
            model_name='work',
            name='memo',
            field=models.TextField(default='', verbose_name='心得'),
        ),
        migrations.AlterField(
            model_name='work',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='works', to=settings.AUTH_USER_MODEL),
        ),
    ]
