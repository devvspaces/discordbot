# Generated by Django 3.2.5 on 2021-07-31 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discordaccount',
            name='user',
        ),
    ]
