# Generated by Django 3.2.5 on 2021-08-02 00:37

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('paygate', '0008_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
