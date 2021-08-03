from mainapp.managers import MessageManager
import uuid

from django.db import models


class BlacklistParent(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def count_list(self):
        return self.blacklist_set.count()

    def __str__(self):
        return str(self.uid)


class Blacklist(models.Model):
    username = models.CharField(max_length=200)
    blacklist_parent = models.ForeignKey(BlacklistParent, on_delete=models.CASCADE)

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

    def get_active_users(self):
        return [x for x in self.member_set.all() if x.is_blacklisted]

    def __str__(self):
        return self.name


class Member(models.Model):
    username = models.CharField(max_length=200)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    discord_server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE)

    # @property
    # def is_blacklisted(self):
    #     for i User.blacklistparent_set.all():
    #         pass

    def __str__(self):
        return self.username


# class MemberServer(models.Model):
#     blacklisted = models.BooleanField(default=False)
#     discord_server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE)
#     member = models.ForeignKey(Member, on_delete=models.CASCADE)
#     uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

#     def __str__(self):
#         return str(self.uid)


# Messages model to keep track the messages sent by user
class DirectMessage(models.Model):
    server = models.ForeignKey(DiscordServer, on_delete=models.DO_NOTHING, null=True)
    blacklist = models.ForeignKey(BlacklistParent, on_delete=models.DO_NOTHING, null=True)
    message = models.TextField()
    delay = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    add_users = models.BooleanField(default=False)
    message_stop = models.IntegerField()
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sent = models.IntegerField(default=0)

    objects = MessageManager()

    def __str__(self):
        return str(self.uid)