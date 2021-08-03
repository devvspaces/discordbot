# Generated by Django 3.2.5 on 2021-07-31 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paygate', '0007_auto_20210727_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('1', 'Pending'), ('2', 'Completed'), ('3', 'Cancelled')], default='1', max_length=10),
        ),
    ]
