# Generated by Django 3.2.6 on 2021-08-20 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_discordaccount_use_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProxyPort',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_port', models.CharField(max_length=200)),
                ('active', models.BooleanField(default=False)),
                ('use_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='discordaccount',
            name='expired_token',
            field=models.BooleanField(default=False),
        ),
    ]
