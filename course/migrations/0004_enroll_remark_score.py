# Generated by Django 2.2.15 on 2020-08-10 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_auto_20200708_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='enroll',
            name='remark_score',
            field=models.IntegerField(default=0, verbose_name='心得成績'),
        ),
    ]