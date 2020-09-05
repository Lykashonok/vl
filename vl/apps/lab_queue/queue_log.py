import datetime
class QueueLogger(object):

    actions = [
        'left',
        'move_user_up',
        'move_user_down',
        'enter',
        'kick',
        'edit_queue',
    ]

    @staticmethod
    def createLog(action, queue_id, *args, **kwargs):
        log_time = datetime.datetime.now()
        if action and queue_id:
            log_string = ''
            if action == 'enter':
                user = kwargs['user']
                log_string = '[{0}] Пользователь [{1} {2} id:{3} email:{4}] вошёл в очередь'.format(log_time, user.first_name, user.last_name, user.id, user.email)
            elif action == 'left':
                log_string = '[{0}] Пользователь [{1} {2} id:{3} email:{4}] покинул очередь'.format(log_time, user.first_name, user.last_name, user.id, user.email)
            else:
                raise 'Invalid action'
        else:
            raise 'Must have action type and queue_ide'

