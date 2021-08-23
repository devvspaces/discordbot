import uuid

from django.db import models

from .managers import OrderManager

class Order(models.Model):
    STATUS = [
        ('1', 'Pending', ),
        ('2', 'Completed', ),
        ('3', 'Cancelled', ),
    ]
    profile = models.ForeignKey('account.Profile', on_delete=models.CASCADE)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    dm_amount = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS, default='1')
    created = models.DateTimeField(auto_now_add=True)

    objects = OrderManager()

    def profile_name(self):
        return self.profile.discord_username

    def __str__(self):
        return str(self.order_id)


class Package(models.Model):
    amount = models.IntegerField()
    description = models.TextField(default='This package credits you the amount of messages bought to help you message more users')
    price = models.FloatField()
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.uid)