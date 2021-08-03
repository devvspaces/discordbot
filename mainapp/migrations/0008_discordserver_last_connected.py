# Generated by Django 3.2.5 on 2021-08-01 00:48

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0007_auto_20210801_0145'),
    ]

    operations = [
        migrations.AddField(
            model_name='discordserver',
            name='last_connected',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 8, 1, 0, 48, 35, 168047, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
