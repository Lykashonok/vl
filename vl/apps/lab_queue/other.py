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