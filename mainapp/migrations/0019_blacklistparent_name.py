# Generated by Django 3.2.6 on 2021-08-20 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0018_blacklist_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='blacklistparent',
            name='name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]