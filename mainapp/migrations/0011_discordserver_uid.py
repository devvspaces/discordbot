# Generated by Django 3.2.5 on 2021-08-02 05:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0010_auto_20210802_0655'),
    ]

    operations = [
        migrations.AddField(
            model_name='discordserver',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
