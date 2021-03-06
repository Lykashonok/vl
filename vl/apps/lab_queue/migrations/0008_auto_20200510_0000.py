# Generated by Django 3.0.5 on 2020-05-10 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab_queue', '0007_auto_20200509_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinqueue',
            name='uiq_first_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='имя пользователя'),
        ),
        migrations.AddField(
            model_name='userinqueue',
            name='uiq_group',
            field=models.IntegerField(blank=True, default=0, verbose_name='группа пользователя'),
        ),
        migrations.AddField(
            model_name='userinqueue',
            name='uiq_second_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='фамилия пользователя'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user_group',
            field=models.IntegerField(blank=True, verbose_name='группа пользователя'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user_type',
            field=models.CharField(blank=True, max_length=20, verbose_name='тип пользователя'),
        ),
        migrations.AlterField(
            model_name='userinqueue',
            name='uiq_info',
            field=models.TextField(blank=True, default='', verbose_name='дополнительная информация'),
        ),
    ]
