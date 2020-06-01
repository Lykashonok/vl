from django.contrib import admin

# Register your models here.

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Queue, Profile, UserInQueue, Message, Chat, EmailConfirmed
from .admin_custom import send_mail_view

from django.shortcuts import render
from .forms import SendMailForm
from vl.settings import EMAIL_HOST_USER
from django.urls import path
from django.http import HttpResponseRedirect

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
    inlines = (ProfileInline, EmailConfirmedInline, )

    change_list_template = 'admin/change_list_with_mail.html'

    def send_mail_to_users(self, request, queryset):
        mail_send_form = SendMailForm()
        context = {
            'users':list(queryset),
            'form': mail_send_form
        }
        if request.method == "POST":
            if 'send_mail_subject' in request.POST or 'send_mail_text' in request.POST:
                send_mail_subject = request.POST.get('send_mail_subject')
                send_mail_text = request.POST.get('send_mail_text')
                mails = []
                for mail in queryset: mails.append(queryset.email)
                to_list = [*mail, EMAIL_HOST_USER]
                print(to_list)
        return HttpResponseRedirect("../")
    
    send_mail_to_users.short_description = 'Отправить письмо на почту следующим пользователям'

    actions = [send_mail_to_users,]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('mailSend/<int:mailSubject>/', self.send_mail_to_users)
        ]
        return custom_urls + urls

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