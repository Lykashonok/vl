# Generated by Django 3.0.5 on 2020-05-18 19:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lab_queue', '0017_auto_20200518_2204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queue',
            name='queue_enter_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='дата и время открытия очереди'),
        ),
    ]