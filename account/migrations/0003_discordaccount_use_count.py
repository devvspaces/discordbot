# Generated by Django 3.2.5 on 2021-08-02 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_remove_discordaccount_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='discordaccount',
            name='use_count',
            field=models.IntegerField(default=0),
        ),
    ]