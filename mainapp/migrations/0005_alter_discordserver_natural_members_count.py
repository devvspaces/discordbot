# Generated by Django 3.2.5 on 2021-07-31 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_discordserver_natural_members_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discordserver',
            name='natural_members_count',
            field=models.IntegerField(default=0),
        ),
    ]
