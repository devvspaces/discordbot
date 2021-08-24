from django.db import models


class MostUnused(object):
    def most_unused(self):
        # Get the active ones only
        queryset = self.filter(active=True)
        
        # Find the discord account instance that is most unused
        min_value = queryset.first().use_count if queryset.first() else 0
        min_instance = ''
        for i in self:
            if i.use_count <= min_value:
                min_value = i.use_count
                min_instance = i
        
        return min_instance

class DiscordAccountQuery(models.QuerySet, MostUnused):
    pass
        

class DiscordAccountManager(models.Manager):
    def get_queryset(self):
        return DiscordAccountQuery(model=self.model, using=self._db)
    def most_unused(self):
        return self.get_queryset().filter(expired_token=False).most_unused()


class ProxyPortQuery(models.QuerySet, MostUnused):
    pass

class ProxyPortManager(models.Manager):
    def get_queryset(self):
        return ProxyPortQuery(model=self.model, using=self._db)
    def most_unused(self):
        return self.get_queryset().most_unused()