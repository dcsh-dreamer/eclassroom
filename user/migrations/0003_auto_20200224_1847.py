# Generated by Django 2.2.10 on 2020-02-24 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20200223_2349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='course',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notices', to='course.Course'),
        ),
        migrations.AlterField(
            model_name='messagestatus',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='user.Message'),
        ),
    ]
