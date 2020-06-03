from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.contrib.postgres.indexes import BrinIndex


from django.template.loader import render_to_string
from django.utils.html import strip_tags
# Create your models here.


class Queue(models.Model):
    queue_id = models.AutoField(primary_key=True, db_index=True)
    queue_title = models.CharField('название очереди', max_length=100)
    queue_group = models.IntegerField('номер группы')
    queue_info = models.TextField('дополнительная информация', blank=True)
    queue_create_date = models.DateTimeField(
        'дата создания', auto_now_add=True, blank=True)
    queue_enter_date = models.DateTimeField(
        'дата и время открытия очереди', default=timezone.now, blank=False)
    queue_priorities = ArrayField(models.CharField(
        max_length=50, blank=True), default=list, blank=True)
    queue_sort_by_enter_time = models.BooleanField(
        'сортировать по времени вхождения', blank=True, default=False)

    def __str__(self):
        return f'{self.queue_id} {self.queue_title}'

    class Meta:
        verbose_name = 'Queue'
        verbose_name_plural = 'Queues'
        indexes = (
            BrinIndex(fields=['queue_id']),
        )


class UserInQueue(models.Model):
    queue_id = models.AutoField(primary_key=True, db_index=True)
    uiq_user_id = models.IntegerField('id пользователя')
    uiq_queue_id = models.ForeignKey(Queue, on_delete=models.CASCADE)
    uiq_info = models.TextField(
        'дополнительная информация', blank=True, default='')
    uiq_group = models.IntegerField(
        'группа пользователя', blank=True, default=0)
    uiq_first_name = models.CharField(
        'имя пользователя', max_length=100, blank=True, default='')
    uiq_second_name = models.CharField(
        'фамилия пользователя', max_length=100, blank=True, default='')
    uiq_want_to_swap = models.BooleanField(
        'хочет ли поменяться местами', blank=True, default=False)
    uiq_index = models.IntegerField(
        'порядковый номер в очереди', blank=False, default=0)
    uiq_priorities = ArrayField(models.CharField(
        max_length=50, blank=True), default=list, blank=True)

    def __str__(self):
        return f'user {self.uiq_user_id} in queue {self.uiq_queue_id}'

    class Meta:
        verbose_name = 'User in queue'
        verbose_name_plural = 'Users in queues'
        indexes = (
            BrinIndex(fields=['queue_id']),
        )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #teacher, headman, student
    user_type = models.CharField('тип пользователя', max_length=20, blank=True)
    user_group = models.IntegerField('группа пользователя', blank=True)

    def __str__(self):
        return f'{self.user} {self.user_type} {self.user_group}'

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

class EmailConfirmed(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_activation_key = models.CharField(max_length=200, db_index=True)
    user_verified = models.BooleanField('активирован ли аккаунт', default=False)

    def __str__(self):
        return str(self.user_verified)

    class Meta:
        verbose_name = 'Email Confirmed'
        verbose_name_plural = 'Emails Confirmed'
        indexes = (
            BrinIndex(fields=['user_activation_key']),
        )
    
    def activate_user_email(self, request):
        # https://labqueueisp.herokuapp.com/lab_queue/
        user_activation_url = '/lab_queue/activation/%s'%(self.user_activation_key)
        context = {
            'user_activation_key': self.user_activation_key,
            'user_activation_url': user_activation_url,
            'request': request
        }
        subject = 'Подтверждение аккаунта на сайте с очередями'
        message = render_to_string('lab_queue/activation.html', context)
        to_list = [self.user.email, settings.EMAIL_HOST, ]
        self.email_user(subject, message,settings.EMAIL_HOST, settings.EMAIL_HOST_USER)

    def email_user(self, subject, message, from_email='From <labqueueisp@gmail.com>', *args, **kwargs):
        send_mail(subject, message, from_email, [self.user.email], **kwargs)

    

class Chat(models.Model):
    chat_id = models.AutoField(primary_key=True, db_index=True)
    chat_queue_id = models.ForeignKey(Queue, on_delete=models.CASCADE)

    def __str__(self):
        return f'Chat with id: {self.chat_id} in queue with id: {self.chat_queue_id}'

    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'
        indexes = (
            BrinIndex(fields=['chat_id']),
        )

class Message(models.Model):
    message_id = models.AutoField(primary_key=True, db_index=True)
    message_chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE)
    message_user_id = models.IntegerField('id отправителя', blank=False)
    message_text = models.CharField('текст сообщения', max_length=1000, blank=True, default='')
    message_date = models.DateTimeField('дата отправления', auto_now_add=True, blank=True)

    def __str__(self):
        return f'Message with id: {self.message_id} in queue with id: {self.message_chat_id}'

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        indexes = (
            BrinIndex(fields=['message_id']),
        )