def swap_instances_index(fisrt_instance, second_instance):
    tmp = fisrt_instance.uiq_index
    fisrt_instance.uiq_index = second_instance.uiq_index
    second_instance.uiq_index = tmp
    fisrt_instance.uiq_want_to_swap = False
    second_instance.uiq_want_to_swap = False
    return fisrt_instance, second_instance

import re
def is_mobile(request_meta):
    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request_meta):
        return True
    else:
        return False

import random
import hashlib

def get_hash(email):
    short_hash = hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()[:5]
    base, domain = str(email).split('@')
    user_activation_key = hashlib.md5(str(short_hash+base).encode('utf-8')).hexdigest()
    return user_activation_key

from django.core.mail import send_mail
def solo_send_mail(mail):
    send_mail(mail['mailSubject'], mail['mailText'], 'from <labqueueisp@gmail.com>', [mail['mail'],])


import sys
import logging

from django.core.management.color import color_style

class DjangoColorsFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super(DjangoColorsFormatter, self).__init__(*args, **kwargs)
        self.style = self.configure_style(color_style())

    def configure_style(self, style):
        style.DEBUG = style.HTTP_NOT_MODIFIED
        style.INFO = style.HTTP_INFO
        style.WARNING = style.HTTP_NOT_FOUND
        style.ERROR = style.ERROR
        style.CRITICAL = style.HTTP_SERVER_ERROR
        return style

    def format(self, record):
        message = logging.Formatter.format(self, record)
        if sys.version_info[0] < 3:
            if isinstance(message, str):
                message = message.encode('utf-8')
        colorizer = getattr(self.style, record.levelname, self.style.HTTP_SUCCESS)
        return colorizer(message)