import uuid

from django.db import models

from account.models import DiscordAccount
from mainapp.models import DirectMessage, DiscordServer


class SeleniumBot(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    messages = models.ManyToManyField(DirectMessage)
    servers = models.ManyToManyField(DiscordServer)
    discord_account = models.OneToOneField(DiscordAccount, on_delete=models.DO_NOTHING, null=True)


    def __str__(self):
        return str(self.uid)