from mainapp.managers import MessageManager
import uuid

from django.db import models
from django.urls import reverse


class BlacklistParent(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, blank=True)

    def count_list(self):
        return self.blacklist_set.count()
    
    def gen_name(self):
        return self.name if self.name else f'Blacklist {self.id}'.capitalize()

    def __str__(self):
        return str(self.uid)

    def get_absolute_url(self):
        return reverse("dashboard:blacklist_view", kwargs={"uid": str(self.uid)})


class Blacklist(models.Model):
    username = models.CharField(max_length=200)
    blacklist_parent = models.ForeignKey(BlacklistParent, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class DiscordServer(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    link = models.URLField()
    icon = models.URLField(blank=True)
    name = models.CharField(max_length=200)
    members = models.IntegerField(default=0)
    last_connected = models.DateTimeField(auto_now_add=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def count_members(self):
        return self.member_set.count()

    def __str__(self):
        return self.name
    
    def get_uid(self):
        return str(self.uid)

    def get_absolute_url(self):
        return reverse("dashboard:discord_server", kwargs={"uid": self.get_uid()})
    


class Member(models.Model):
    username = models.CharField(max_length=200)
    image = models.URLField(blank=True)
    roles = models.TextField(max_length=700, default='Member')
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    discord_server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


# Messages model to keep track the messages sent by user
class DirectMessage(models.Model):
    profile = models.ForeignKey('account.Profile', on_delete=models.CASCADE)
    server = models.ForeignKey(DiscordServer, on_delete=models.DO_NOTHING, null=True)
    server_name = models.CharField(max_length=200, blank=True)
    blacklist = models.ForeignKey(BlacklistParent, on_delete=models.DO_NOTHING, null=True, blank=True)
    message = models.TextField()
    delay = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    add_users = models.BooleanField(default=False)
    blacklist_users = models.BooleanField(default=False)
    message_stop = models.IntegerField(default=0)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sent = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

    event_stop = models.BooleanField(default=False)

    objects = MessageManager()

    def isSet(self):
        return self.event_stop

    def setStop(self):
        self.event_stop = True
        self.completed = True
        self.save()

    # override save method to add server_name when model is saved
    def save(self, *args, **kwargs):
        if self.server:
            self.server_name = self.server.name
        
        super().save( *args, **kwargs)

    def __str__(self):
        return str(self.uid)