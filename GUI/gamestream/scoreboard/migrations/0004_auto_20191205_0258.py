# Generated by Django 3.0 on 2019-12-05 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scoreboard', '0003_metateam_health'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='metateam',
            name='health',
        ),
        migrations.AddField(
            model_name='robot',
            name='health',
            field=models.IntegerField(default=24),
        ),
    ]
