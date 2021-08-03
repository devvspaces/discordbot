from django.db import models

class DiscordAccountQuery(models.QuerySet):
    def most_unused(self):
        # Find the discord account instance that is most unused
        min_value = self.first().use_count if self.first() else 0
        min_instance = ''
        for i in self:
            if i.use_count <= min_value:
                min_value = i.use_count
                min_instance = i
        
        
        return min_instance

class DiscordAccountManager(models.Manager):
    def get_queryset(self):
        return DiscordAccountQuery(model=self.model, using=self._db)
    def most_unused(self):
        return self.get_queryset().most_unused()