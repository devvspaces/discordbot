from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Profile, DiscordAccount, ProxyPort
from .forms import UserRegisterForm


class UserAdmin(BaseUserAdmin):
	# The forms to add and change user instances
	# form = UserUpdateForm
	add_form = UserRegisterForm

	# The fields to be used in displaying the User model.
	# These override the definitions on the base UserAdmin
	# that reference specific fields on auth.User.
	list_display=('email', 'discord_username', 'active',)
	list_filter = ('active','staff','admin',)
	search_fields=['email']
	fieldsets = (
		('User', {'fields': ('email', 'password')}),
		('Permissions', {'fields': ('admin','staff','active',)}),
	)
	# add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
	# overrides get_fieldsets to use this attribute when creating a user.
	add_fieldsets = (
		(None, {
                'classes': ('wide',),
                'fields': ('email', 'password',)
            }
		),
	)
	ordering = ('email',)
	filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(DiscordAccount)
admin.site.register(ProxyPort)