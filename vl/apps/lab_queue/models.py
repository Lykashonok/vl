from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Queue(models.Model):
    queue_id = models.AutoField(primary_key=True)
    queue_title = models.CharField('название очереди', max_length = 100)
    queue_group = models.IntegerField('номер группы')
    queue_info = models.TextField('дополнительная информация')
    queue_create_date = models.DateTimeField('дата создания', auto_now_add = True, blank = True)
    queue_enter_date = models.DateTimeField('дата и время открытия очереди', default= timezone.now(), blank = False)
    
    def __str__(self):
        return f'{self.queue_id} {self.queue_title}'

    class Meta:
        verbose_name = 'Queue'
        verbose_name_plural = 'Queues'

class UserInQueue(models.Model):
    queue_id = models.AutoField(primary_key=True)
    uiq_user_id = models.IntegerField('id пользователя')
    uiq_queue_id = models.ForeignKey(Queue, on_delete = models.CASCADE)
    uiq_info = models.TextField('дополнительная информация', blank=True, default='')
    uiq_group = models.IntegerField('группа пользователя', blank=True, default=0)
    uiq_first_name = models.CharField('имя пользователя', max_length = 100, blank=True, default='')
    uiq_second_name = models.CharField('фамилия пользователя', max_length = 100, blank=True, default='')
    uiq_want_to_swap = models.BooleanField('хочет ли поменяться местами', blank=True, default=False)
    uiq_index = models.IntegerField('порядковый номер в очереди', blank=False, default=0)


    def __str__(self):
        return f'user {self.uiq_user_id} in queue {self.uiq_queue_id}'

    class Meta:
        verbose_name = 'User in queue'
        verbose_name_plural = 'Users in queues'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #teacher, headman, student
    user_type = models.CharField('тип пользователя', max_length = 20, blank=True)
    user_group = models.IntegerField('группа пользователя', blank=True)

    def __str__(self):
        return f'{self.user} {self.user_type} {self.user_group}'
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'