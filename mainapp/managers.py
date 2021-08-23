from django.db import models

class MessageQuery(models.QuerySet):
    def count_sent(self):
        # Loop through all the queryset and sum up sents
        n = sum([i.sent for i in self])
        # for i in self:
        #     n += i.sent
        return n

class MessageManager(models.Manager):
    def get_queryset(self):
        return MessageQuery(model=self.model, using=self._db)
    def count_sent(self):
        return self.get_queryset().count_sent()