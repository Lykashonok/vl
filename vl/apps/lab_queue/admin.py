from django.contrib import admin

# Register your models here.

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Queue, Profile, UserInQueue, Message, Chat, EmailConfirmed

from .forms import SendMailForm
from vl.settings import EMAIL_HOST_USER
from django.urls import path
from django.http import HttpResponseRedirect
from multiprocessing import Pool, cpu_count
from django.core.mail import send_mail
from .other import solo_send_mail
import re

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
    list_display= ('id','username','email','first_name','last_name','user_type','user_group')
    change_list_template = 'admin/change_list_with_mail.html'

    def user_type(self, obj):
        return f"{obj.profile.user_type}"

    def user_group(self, obj):
        return f"{obj.profile.user_group}"

    def send_mail_to_users(self, request, mailSubject, mailText, emails):
        mail_send_form = SendMailForm()
        context = {
            # 'users':list(queryset),
            'form': mail_send_form
        }
        if request.method == "POST":
            print(mailSubject, mailText, emails)
            emails = list(filter(lambda email: re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$',email), emails.split(',')))
            if len(emails) != 0 and mailSubject and mailText:
                print(request.POST)
                to_list = [*emails,] #EMAIL_HOST_USER]
                mails_to_send = []
                for mail in emails: mails_to_send.append({"mailSubject" : request.POST.get('mailSubject'), "mailText" : request.POST.get('mailText'), "mail": mail})
                pool = Pool(processes=cpu_count())
                pool.map(solo_send_mail, mails_to_send)
                    
        return HttpResponseRedirect("../../../../")
    
    send_mail_to_users.short_description = 'Отправить письмо на почту следующим пользователям'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('mailSend/<str:mailSubject>/<str:mailText>/<str:emails>/', self.send_mail_to_users),
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