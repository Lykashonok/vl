from django.contrib import admin

# Register your models here.

from .models import Queue, Profile, UserInQueue

admin.site.register(Queue)
admin.site.register(Profile)
admin.site.register(UserInQueue)