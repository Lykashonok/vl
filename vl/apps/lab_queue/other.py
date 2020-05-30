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