from django.contrib import admin

from .models import DiscordServer, DirectMessage, Member, BlacklistParent, Blacklist


class MemberInline(admin.TabularInline):
    model = Member

class DiscordServerAdmin(admin.ModelAdmin):

    inlines = [
        MemberInline,
    ]


admin.site.register(DiscordServer, DiscordServerAdmin)
admin.site.register(DirectMessage)
admin.site.register(Member)
admin.site.register(BlacklistParent)
admin.site.register(Blacklist)