# Generated by Django 2.2.10 on 2020-02-23 03:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='主旨')),
                ('body', models.TextField(verbose_name='內容')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='時間')),
                ('course', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to='course.Course')),
                ('recipient', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outbox', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MessageStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read', models.DateTimeField(auto_now_add=True, verbose_name='閱讀時間')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='user.Message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
