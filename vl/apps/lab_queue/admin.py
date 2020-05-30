from django.contrib import admin

# Register your models here.

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Queue, Profile, UserInQueue, Message, Chat, EmailConfirmed

class MessageInline(admin.TabularInline):
    model = Message

class MessageAdmin(admin.ModelAdmin):
    inlines = [
        MessageInline
    ]

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'
    fk_name = 'user'

class EmailConfirmedInline(admin.StackedInline):
    model = EmailConfirmed
    can_delete = False
    verbose_name_plural = 'EmailConfirmed'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, EmailConfirmedInline,)
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Queue)
admin.site.register(UserInQueue)
admin.site.register(Message)
admin.site.register(Chat, MessageAdmin)