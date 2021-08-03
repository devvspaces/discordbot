from django.db import models

class OrderQuery(models.QuerySet):
    def count_dm(self):
        # Loop through all the queryset and sum up sents
        queryset = self.filter(status='2')
        n = 0
        for i in queryset:
            n += i.dm_amount
        return n

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuery(model=self.model, using=self._db)
    def count_dm(self):
        return self.get_queryset().count_dm()