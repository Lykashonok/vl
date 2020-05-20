# Generated by Django 3.0.5 on 2020-05-14 19:28

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('lab_queue', '0012_auto_20200511_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='queue_enter_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 5, 14, 19, 28, 28, 507790, tzinfo=utc), verbose_name='дата и время открытия очереди'),
        ),
    ]