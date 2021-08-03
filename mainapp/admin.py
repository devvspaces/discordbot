from django.contrib import admin

from .models import DiscordServer, DirectMessage, Member


admin.site.register(DiscordServer)
admin.site.register(DirectMessage)
admin.site.register(Member)