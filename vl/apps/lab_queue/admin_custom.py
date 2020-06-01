from django.shortcuts import render
from multiprocessing import cpu_count, Pool
from .forms import SendMailForm
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from .forms import SendMailForm
from vl.settings import EMAIL_HOST_USER

def send_mail_view(request, queryset):
    mail_send_form = SendMailForm()
    context = {
        'users':list(queryset),
        'form': mail_send_form
    }

    print('aloha')
    if request.method == "POST":
        print('it went in')
    #     send_mail(subject, message, from_email, [self.user.email], **kwargs)
        mail_send_form = SendMailForm(request.POST)
        print(request.POST)
        print(mail_send_form)
        if mail_send_form.is_valid():
            send_mail_subject = mail_send_form.cleaned_data.get('send_mail_subject')
            send_mail_text = mail_send_form.cleaned_data.get('send_mail_text')
            mails = []
            for mail in queryset: mails.append(queryset.email)
            to_list = [*mail, EMAIL_HOST_USER]
            print(to_list)



    return render(request, 'admin/mail.html', context)