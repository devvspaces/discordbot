# Generated by Django 3.2.6 on 2021-08-15 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0016_auto_20210813_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directmessage',
            name='blacklist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='mainapp.blacklistparent'),
        ),
    ]
