def swap_instances_index(fisrt_instance, second_instance):
    tmp = fisrt_instance.uiq_index
    fisrt_instance.uiq_index = second_instance.uiq_index
    second_instance.uiq_index = tmp
    fisrt_instance.uiq_want_to_swap = False
    second_instance.uiq_want_to_swap = False
    return fisrt_instance, second_instance