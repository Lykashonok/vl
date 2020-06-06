from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse

from django import forms
from django.utils import timezone

from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.forms import formset_factory

from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm, ProfileForm, QueueEnterForm, ChangeQueueIndexForm, ChangeInfoForm, NewQueueForm, ConfirmForm, EditQueueForm, EditUserForm, PriorityForm, StatusCheckBoxField, PriorityChoiceForm

from .other import swap_instances_index, is_mobile, get_hash

from django.contrib.auth.models import User
from .models import Queue, UserInQueue, Profile, Message, Chat, EmailConfirmed
from django.contrib.auth.decorators import login_required


def index(request):
    overall_list = Queue.objects.order_by('queue_create_date')
    return render(request, 'lab_queue/mainlist.html', {'overall_list': overall_list})


@login_required
def detail(request, queue_id):
    try:
        queue_enter_form = QueueEnterForm()
        queue_sort_by_enter_date_form = StatusCheckBoxField()

        queue = Queue.objects.get(queue_id=queue_id)
        
        queue_priorities = []
        for choice in queue.queue_priorities: queue_priorities.append(list(eval(choice))[1])

        try:
            chat = Chat.objects.get(chat_queue_id=queue_id)
        except:
            chat = Chat(chat_queue_id=queue)
            chat.save()
            

        user_can_enter = timezone.now() > queue.queue_enter_date
        user_can_enter_remain = queue.queue_enter_date - timezone.now()
        users = UserInQueue.objects.filter(
            uiq_queue_id=queue_id).order_by('uiq_index')
        current_user = list(
            filter(lambda item: item.uiq_user_id == request.user.id, users))
        context = {
            'queue': queue,
            'users': users,
            'user_can_enter': user_can_enter,
            'user_can_enter_remain': user_can_enter_remain,
            'queue_priorities' : queue_priorities
        }
        if request.method == 'POST':
            if 'queue_enter' in request.POST:
                queue_enter_form = QueueEnterForm(request.POST)
                if len(current_user) != 0:
                    # context.update({
                    #     'current_user': current_user[0],
                    #     'queue_enter_form': queue_enter_form
                    # })
                    return render(request, 'lab_queue/detail.html', context)
                info = queue_enter_form.cleaned_data.get(
                    'uiq_info') if queue_enter_form.is_valid() else ''
                
                
                priorities, chosen_priorities_labels = [],[]
                for choice in queue.queue_priorities: priorities.append(list(eval(choice)))
                for chosen in request.POST.getlist('choices'):
                    for item in priorities:
                        if item[0] == chosen:
                            chosen_priorities_labels.append(item[1])
                new_user_in_queue = UserInQueue(
                    uiq_user_id=request.user.id,
                    uiq_queue_id=queue,
                    uiq_info=info,
                    uiq_group=request.user.profile.user_group,
                    uiq_first_name=request.user.first_name,
                    uiq_second_name=request.user.last_name,
                    uiq_priorities=chosen_priorities_labels,
                    uiq_index=len(users) + 1
                )
                messages.success(
                    request, f'{request.user.first_name}, Вы вошли в очередь, удачи подождать.')
                new_user_in_queue.save()
            elif 'queue_exit' in request.POST:
                user_to_exit = UserInQueue.objects.get(
                    uiq_user_id=request.user.id, uiq_queue_id=queue_id)
                other_users = UserInQueue.objects.filter(
                    uiq_queue_id=user_to_exit.uiq_queue_id, uiq_index__gt=user_to_exit.uiq_index)
                for user in other_users:
                    user.uiq_index -= 1
                    user.save()
                user_to_exit.delete()
                messages.success(
                    request, f'{request.user.first_name}, Вы успешно покинули очередь, хоть и непонятно зачем.')
            elif 'queue_swap_state' in request.POST:
                user_to_swap = UserInQueue.objects.filter(
                    uiq_user_id=request.user.id, uiq_queue_id=queue_id)
                value = user_to_swap[0].uiq_want_to_swap
                if value:
                    user_to_swap.update(uiq_want_to_swap=False)
                else:
                    user_to_swap.update(uiq_want_to_swap=True)
            elif 'queue_swap' in request.POST:
                form = ChangeQueueIndexForm(request.POST)
                if form.is_valid():
                    queue_swap_id = form.cleaned_data.get('queue_swap')
                    user_to_swap = UserInQueue.objects.filter(
                        uiq_user_id=queue_swap_id, uiq_queue_id=queue_id)[0]
                    user = UserInQueue.objects.filter(
                        uiq_user_id=request.user.id, uiq_queue_id=queue_id)[0]
                    if user_to_swap.uiq_want_to_swap:
                        user, user_to_swap = swap_instances_index(
                            user, user_to_swap)
                        user_to_swap.save()
                        user.save()
                        messages.success(
                            request, f'{request.user.first_name}, у Вас получилось поменяться местами!')
                    else:
                        messages.error(
                            request, f'{request.user.first_name}, не получилось поменяться местами!')
            elif 'queue_change_info' in request.POST:
                form = ChangeInfoForm(request.POST)
                if form.is_valid():
                    uiq_info = form.cleaned_data.get('uiq_info')
                    uiq_user = UserInQueue.objects.filter(uiq_user_id=request.user.id, uiq_queue_id=queue_id)[0]

                    priorities, chosen_priorities_labels = [],[]
                    for choice in queue.queue_priorities: priorities.append(list(eval(choice)))
                    for chosen in request.POST.getlist('choices'):
                        for item in priorities:
                            if item[0] == chosen:
                                chosen_priorities_labels.append(item[1])

                    uiq_user.uiq_priorities = chosen_priorities_labels
                    uiq_user.uiq_info = uiq_info
                    uiq_user.save()
                    messages.success(request, f'{request.user.first_name}, вы изменили дополнительную информацию.')
            elif 'queue_move_up' in request.POST:
                form = ChangeQueueIndexForm(request.POST)
                if form.is_valid():
                    queue_swap_id = form.cleaned_data.get('queue_move_up')
                    user = UserInQueue.objects.filter(
                        uiq_user_id=queue_swap_id, uiq_queue_id=queue_id)[0]
                    user_to_swap = UserInQueue.objects.filter(
                        uiq_queue_id=user.uiq_queue_id, uiq_index=int(user.uiq_index) - 1)
                    if len(user_to_swap) != 0:
                        user_to_swap = user_to_swap[0]
                        user, user_to_swap = swap_instances_index(
                            user, user_to_swap)
                        user.save()
                        user_to_swap.save()
                        messages.success(
                            request, f'{request.user.first_name}, Вы успешно поменяли местами.')
                    else:
                        messages.error(
                            request, f'{request.user.first_name}, не получилось поменять местами!')
            elif 'queue_move_down' in request.POST:
                form = ChangeQueueIndexForm(request.POST)
                if form.is_valid():
                    queue_swap_id = form.cleaned_data.get('queue_move_down')
                    user = UserInQueue.objects.filter(
                        uiq_user_id=queue_swap_id, uiq_queue_id=queue_id)[0]
                    user_to_swap = UserInQueue.objects.filter(
                        uiq_queue_id=user.uiq_queue_id, uiq_index=int(user.uiq_index) + 1)
                    if len(user_to_swap) != 0:
                        user_to_swap = user_to_swap[0]
                        user, user_to_swap = swap_instances_index(
                            user, user_to_swap)
                        user.save()
                        user_to_swap.save()
                        messages.success(
                            request, f'{request.user.first_name}, Вы успешно поменяли местами.')
                    else:
                        messages.error(
                            request, f'{request.user.first_name}, не получилось поменять местами!')
            elif 'queue_delete_start' in request.POST:
                form = ConfirmForm(request.POST)
                if form.is_valid():
                    context.update({'queue_delete_start': True})
                    return render(request, 'lab_queue/detail.html', context)
            elif 'queue_delete_confirm_true' in request.POST:
                form = ConfirmForm(request.POST)
                if form.is_valid():
                    uiq_queue_id = form.cleaned_data.get(
                        'queue_delete_confirm_true')
                    queue_to_delete = Queue.objects.get(queue_id=uiq_queue_id)
                    if queue_to_delete:
                        queue_to_delete.delete()
                        messages.success(
                            request, f'{request.user.first_name}, Вы успешно удалили очередь.')
                    else:
                        messages.error(
                            request, f'{request.user.first_name}, удалить не получилось, возможно, её уже нет!')
                    context = {'overall_list': Queue.objects.order_by(
                        'queue_create_date')}
                    return render(request, 'lab_queue/mainlist.html', context)
            elif 'queue_delete_confirm_false' in request.POST:
                form = ConfirmForm(request.POST)
                if form.is_valid():
                    context.update({'queue_delete_start': False})
                    return render(request, 'lab_queue/detail.html', context)
            elif 'sort_by_enter_time_change' in request.POST:
                Queue.objects.filter(queue_id=queue_id).update(
                    queue_sort_by_enter_time=not queue.queue_sort_by_enter_time)
            elif 'queue_priority_move_up' in request.POST or 'queue_priority_move_down' in request.POST:
                index,value_to_find = 0, request.POST.get('queue_priority_move_up') if request.POST.get('queue_priority_move_up') else request.POST.get('queue_priority_move_down')
                for i in range(len(queue_priorities)):
                    if value_to_find == queue_priorities[i]: 
                        index = i
                        break
                if index != 0 and 'queue_priority_move_up' in request.POST:
                    queue.queue_priorities[index], queue.queue_priorities[index - 1] = queue.queue_priorities[index-1], queue.queue_priorities[index]
                    queue.save()
                    messages.success(
                        request, f'{request.user.first_name}, Вы успешно передвинули приоритет.')
                elif index != len(queue.queue_priorities)-1 and 'queue_priority_move_down' in request.POST:
                    queue.queue_priorities[index], queue.queue_priorities[index + 1] = queue.queue_priorities[index+1], queue.queue_priorities[index]
                    queue.save()
                    messages.success(
                        request, f'{request.user.first_name}, Вы успешно передвинули приоритет.')
                else:
                    messages.error(
                        request, f'{request.user.first_name}, удалить не получилось, возможно, её уже нет!')
            elif 'queue_user_delete' in request.POST:
                try:
                    user_to_delete = UserInQueue.objects.get(uiq_queue_id = queue_id, uiq_user_id = request.POST.get('queue_user_delete'))
                    other_users = UserInQueue.objects.filter(
                    uiq_queue_id=user_to_delete.uiq_queue_id, uiq_index__gt=user_to_delete.uiq_index)
                    for user in other_users:
                        user.uiq_index -= 1
                        user.save()
                    user_to_delete.delete()
                    messages.success(request, f'{request.user.first_name}, Вы успешно выкинули человека из очереди.')
                except:
                    messages.error(request, f'{request.user.first_name}, удалить не получилось!')
            elif 'queue_message_send' in request.POST:
                try:
                    text = request.POST.get('queue_message_send')
                    if not text: raise
                    message_to_send = Message(
                        message_chat_id = chat, 
                        message_text = text,
                        message_user_id = request.user.id
                    )
                    message_to_send.save()
                    # messages.success(request, f'{request.user.first_name}, Вы отправили сообщение.')
                except:
                    messages.error(request, f'{request.user.first_name}, Вы не отправили сообщение. Пустое сообщение отправить нельзя!')
            return HttpResponseRedirect(reverse('lab_queue:detail',args=(queue_id,)))
    except:
        raise Http404("Не получилось найти очередь. Скорее всего её уже удалили")
    
    chat_messages = Message.objects.filter(message_chat_id = chat.chat_id).order_by('-message_date')
    chat_messages_full = []
    for message in chat_messages:
        user = User.objects.get(id = message.message_user_id)
        chat_messages_full.append({
            "text" : message.message_text,
            "date" : message.message_date,
            "user" :  {
                "first_name" : user.first_name,
                "last_name" : user.last_name,
                "type": user.profile.user_type,
                "id": user.id
            }
        })
    chat_messages = chat_messages_full

    queue = Queue.objects.get(queue_id=queue_id)
    users = list(UserInQueue.objects.filter(uiq_queue_id=queue_id).order_by('uiq_index'))
    current_user = list(filter(lambda item: item.uiq_user_id == request.user.id, users))
    if not queue.queue_sort_by_enter_time:
        prioritized_users = []
        for priority in queue_priorities:
            for user in users:
                if not user: continue
                if priority in user.uiq_priorities:
                    prioritized_users.append(user)
                    users[users.index(user)] = None
        for user in users:
            if user: prioritized_users.append(user)
        users = prioritized_users

    queue_priorities = []
    for choice in queue.queue_priorities: queue_priorities.append(list(eval(choice))[1])

    choices = []
    for choice in queue.queue_priorities: choices.append(list(eval(choice)))
    priorities_form = PriorityChoiceForm(choices=choices)

    # print(is_mobile(request.META['HTTP_USER_AGENT']))
    context = {
        'queue': queue,
        'users': users,
        'user_can_enter': user_can_enter,
        'user_can_enter_remain': user_can_enter_remain,
        'queue_priorities' : queue_priorities,
        'priorities_form': priorities_form,
        'chat_messages' : chat_messages,
        # 'is_mobile' : is_mobile(request.META['HTTP_USER_AGENT'])
    }
    if len(current_user) != 0:
        context.update({'current_user': current_user[0]})
    else:
        context.update({'queue_enter_form': queue_enter_form, })

    return render(request, 'lab_queue/detail.html', context)

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            email_confirmed, is_email_created = EmailConfirmed.objects.get_or_create(user=user)
            if is_email_created:
                email_confirmed.user_activation_key = get_hash(user.email)
                email_confirmed.save()
                EmailConfirmed.activate_user_email(email_confirmed, request)
            first_name = user_form.cleaned_data.get('first_name')
            email = user_form.cleaned_data.get('email')
            messages.success(
                request, f'Аккаунт был создан, удачи постоять в очередях, {first_name}. На вашу почту {email} было отправлено письмо с ссылкой для активации аккаунта. Проверьте почту.')
            return redirect('/lab_queue/login')
        else:
            messages.error(
                request, f'Что-то пошло не так, аккаунт не был создан')
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileForm()
    return render(request, 'lab_queue/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def editqueue(request, queue_id):
    queue = Queue.objects.get(queue_id=queue_id)
    context = {'queue': queue}
    form = EditQueueForm()
    priorities = formset_factory(PriorityForm, extra=1)
    if request.method == 'POST':
        form = EditQueueForm(request.POST)
        if 'queue_priorities_number_set' in request.POST:
            raw_number = request.POST.get('queue_priorities_number')
            number = int(raw_number) if raw_number else 1
            priorities = formset_factory(PriorityForm, extra=number)
        else:
            priorities = priorities(request.POST, request.FILES)
            if form.is_valid() and priorities.is_valid():

                priorities_to_save = []
                enter_date = form.cleaned_data.get('queue_enter_date') if form.cleaned_data.get('queue_enter_date') else timezone.now()
                for item in priorities.forms:priorities_to_save.append(('priority'+str(priorities.forms.index(item)),item.cleaned_data.get('priority')))

                uiq_users = UserInQueue.objects.filter(uiq_queue_id = queue_id)
                if len(uiq_users) != 0: uiq_users.update(uiq_priorities = [])

                queue.queue_priorities = priorities_to_save

                queue.queue_title = form.cleaned_data.get('queue_title')
                queue.queue_group = form.cleaned_data.get('queue_group')
                queue.queue_info = form.cleaned_data.get('queue_info')
                queue.save()
                messages.success(request, f'Описание очереди было изменено')
            return redirect(f'../../{queue.queue_id}')
    else:
        form = EditQueueForm(initial={
            'queue_title': queue.queue_title,
            'queue_group': queue.queue_group,
            'queue_info': queue.queue_info,
            'queue_enter_date': queue.queue_enter_date
        })
    context.update({'form': form, 'priorities': priorities})
    return render(request, 'lab_queue/editqueue.html', context)

@login_required
def newqueue(request):
    form = NewQueueForm(initial={'queue_title': '', 'queue_group': 0})
    priorities = formset_factory(PriorityForm, extra=1)
    if request.method == 'POST':
        if 'queue_priorities_number_set' in request.POST:
            raw_number = request.POST.get('queue_priorities_number')
            number = int(raw_number) if raw_number else 1
            priorities = formset_factory(PriorityForm, extra=number)
        else:
            form = NewQueueForm(request.POST)
            priorities = priorities(request.POST, request.FILES)
            if form.is_valid() and priorities.is_valid():
                priorities_to_save = []
                enter_date = form.cleaned_data.get('queue_enter_date') if form.cleaned_data.get('queue_enter_date') else timezone.now()
                for item in priorities.forms:priorities_to_save.append(('priority'+str(priorities.forms.index(item)),item.cleaned_data.get('priority')))
                queue_to_create = Queue(
                    queue_title=form.cleaned_data.get('queue_title'),
                    queue_group=form.cleaned_data.get('queue_group'),
                    queue_info=form.cleaned_data.get('queue_info'),
                    queue_enter_date=enter_date,
                    queue_priorities=priorities_to_save
                )

                queue_to_create.save()

                overall_list = Queue.objects.order_by('queue_create_date')
                context = {'overall_list': overall_list}

                messages.success(
                    request, f'Очередь была создана, удачи в ней постоять, {request.user.first_name}')
                return render(request, 'lab_queue/mainlist.html', context)
        form = NewQueueForm(request.POST, initial={
            'queue_title': request.POST.get('queue_title'),
            'queue_group': request.POST.get('queue_group'),
            'queue_info': request.POST.get('queue_info'),
            'queue_enter_date': request.POST.get('queue_enter_date'),
        })

    return render(request, 'lab_queue/newqueue.html', {'form': form, 'priorities': priorities})

@login_required
def account(request):
    user_form = EditUserForm()
    profile_form =ProfileForm()
    print('passed1')
    user_form = EditUserForm(initial={
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name
    })
    profile_form = ProfileForm(initial={
        'user_type': request.user.profile.user_type,
        'user_group': request.user.profile.user_group
    })
    if request.method == 'POST':
        if 'edit_account' in request.POST:
            user_form = EditUserForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, instance=request.user.profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, f'Описание аккаунта было изменено')
                return HttpResponseRedirect(reverse('lab_queue:account'))
        elif 'send_verification_account' in request.POST:
            try:
                if not request.user.email: raise
                email_confirmed, is_email_created = EmailConfirmed.objects.get_or_create(user=request.user)
                if email_confirmed:
                    email_confirmed.user_activation_key = get_hash(request.user.email)
                    email_confirmed.save()
                    EmailConfirmed.activate_user_email(email_confirmed, request)
                    user_activation_url = '/lab_queue/activation/%s'%(email_confirmed.user_activation_key)
                    context = {
                        'user_activation_key': email_confirmed.user_activation_key,
                        'user_activation_url': user_activation_url,
                        'request': request
                    }
                    subject = 'Подтверждение аккаунта на сайте с очередями'
                    message = render_to_string('lab_queue/activation.html', context)
                    to_list = [request.user.email, settings.EMAIL_HOST, ]
                    send_mail(subject, message, 'From <labqueueisp@gmail.com>', [request.user.email])
                    messages.success(request, f'Сообщение было отправлено! Проверьте вашу почту')
            except:
                messages.error(request, f'Сообщение не было отправлено, что-то не так с почтой или письмом')
            return HttpResponseRedirect(reverse('lab_queue:account'))
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_confirmed': EmailConfirmed.objects.get_or_create(user=request.user)[0].user_verified
    }
    return render(request, 'lab_queue/account.html', context)

@login_required
def activation(request, user_activation_key):
    context = {'status':'failed'}
    try:
        user_confirmed = EmailConfirmed.objects.get(user_activation_key = user_activation_key)
    except EmailConfirmed.DoesNotExist:
        raise Http404
    if user_confirmed is not None and not user_confirmed.user_verified:
        user_confirmed.user_verified = True
        user_confirmed.save()
        context.update({'status':'success'})
        messages.success(request, f'Аккаунт был подтверждён')
    elif user_confirmed is not None and user_confirmed.user_verified:
        messages.warning(request, f'Аккаунт уже был подтверждён до этого')
        context.update({'status':'already'})
    else:
        context.update({'status':'failed'})
    return render(request, 'lab_queue/activated.html', context)