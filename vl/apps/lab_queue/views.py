from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse

from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm, ProfileForm, QueueEnterForm, ChangeQueueIndexForm, ChangeInfoForm, NewQueueForm
from .other import swap_instances_index

from .models import Queue, UserInQueue, Profile
from django.contrib.auth.decorators import login_required

def index(request):
    overall_list = Queue.objects.order_by('queue_create_date')
    return render(request, 'lab_queue/mainlist.html',
    {
        'overall_list' : overall_list
    })

@login_required
def detail(request, queue_id):
    # try:
    queue_enter_form = QueueEnterForm()
    queue = Queue.objects.get( queue_id = queue_id )
    users = UserInQueue.objects.filter( uiq_queue_id = queue_id).order_by('uiq_index')
    current_user = list(filter(lambda item: item.uiq_user_id == request.user.id, users))

    if request.method == 'POST':
        if 'queue_enter' in request.POST:
            if len(current_user) != 0:
                return render(request, 'lab_queue/detail.html', {
                    'queue': queue, 
                    'users': users, 
                    'current_user': current_user[0],
                })
            queue_enter_form = QueueEnterForm(request.POST)
            info = queue_enter_form.cleaned_data.get('uiq_info') if queue_enter_form.is_valid() else ''
            new_user_in_queue = UserInQueue(
                uiq_user_id = request.user.id,
                uiq_queue_id = queue,
                uiq_info = info,
                uiq_group = request.user.profile.user_group,
                uiq_first_name = request.user.first_name,
                uiq_second_name = request.user.last_name,
                uiq_index = len(users) + 1
            )
            messages.success(request, f'{request.user.first_name}, Вы вошли в очередь, удачи подождать.')
            new_user_in_queue.save()
        elif 'queue_exit' in request.POST:
            user_to_exit = UserInQueue.objects.filter(uiq_user_id = request.user.id)[0]
            other_users = UserInQueue.objects.filter(uiq_queue_id = user_to_exit.uiq_queue_id, uiq_index__gt = user_to_exit.uiq_index)
            for user in other_users:
                user.uiq_index -= 1
                user.save()
            user_to_exit.delete()
            messages.success(request, f'{request.user.first_name}, Вы успешно покинули очередь, хоть и непонятно зачем.')
        elif 'queue_swap_state' in request.POST:
            user_to_swap = UserInQueue.objects.filter(uiq_user_id = request.user.id)
            value = user_to_swap[0].uiq_want_to_swap
            if value:
                user_to_swap.update(uiq_want_to_swap = False)
            else:
                user_to_swap.update(uiq_want_to_swap = True)
        elif 'queue_swap' in request.POST:
            form = ChangeQueueIndexForm(request.POST)
            if form.is_valid():
                queue_swap_id = form.cleaned_data.get('queue_swap')
                user_to_swap = UserInQueue.objects.filter(uiq_user_id = queue_swap_id)[0]
                user = UserInQueue.objects.filter(uiq_user_id = request.user.id)[0]
                if user_to_swap.uiq_want_to_swap:
                    user, user_to_swap = swap_instances_index(user, user_to_swap)
                    user_to_swap.save()
                    user.save()
                    messages.success(request, f'{request.user.first_name}, у Вас получилось поменяться местами!')
                else:
                    messages.error(request, f'{request.user.first_name}, не получилось поменяться местами!')
        elif 'queue_change_info' in request.POST:
            form = ChangeInfoForm(request.POST)
            if form.is_valid():
                uiq_info = form.cleaned_data.get('uiq_info')
                uiq_user = UserInQueue.objects.filter(uiq_user_id = request.user.id)[0]
                uiq_user.uiq_info = uiq_info
                uiq_user.save()
                messages.success(request, f'{request.user.first_name}, вы изменили дополнительную информацию.')
        elif 'queue_move_up' in request.POST:
            form = ChangeQueueIndexForm(request.POST)
            if form.is_valid():
                queue_swap_id = form.cleaned_data.get('queue_move_up')
                user = UserInQueue.objects.filter(uiq_user_id = queue_swap_id)[0]
                user_to_swap = UserInQueue.objects.filter(uiq_queue_id = user.uiq_queue_id, uiq_index = int(user.uiq_index) - 1)
                if len(user_to_swap) != 0:
                    user_to_swap = user_to_swap[0]
                    user, user_to_swap = swap_instances_index(user, user_to_swap)
                    user.save()
                    user_to_swap.save()
                    messages.success(request, f'{request.user.first_name}, Вы успешно поменяли местами.')
                else:
                    messages.error(request, f'{request.user.first_name}, не получилось поменять местами!')
        elif 'queue_move_down' in request.POST:
            form = ChangeQueueIndexForm(request.POST)
            if form.is_valid():
                queue_swap_id = form.cleaned_data.get('queue_move_down')
                user = UserInQueue.objects.filter(uiq_user_id = queue_swap_id)[0]
                user_to_swap = UserInQueue.objects.filter(uiq_queue_id = user.uiq_queue_id, uiq_index = int(user.uiq_index) + 1)
                if len(user_to_swap) != 0:
                    user_to_swap = user_to_swap[0]
                    user, user_to_swap = swap_instances_index(user, user_to_swap)
                    user.save()
                    user_to_swap.save()
                    messages.success(request, f'{request.user.first_name}, Вы успешно поменяли местами.')
                else:
                    messages.error(request, f'{request.user.first_name}, не получилось поменять местами!')
    # except:
    #     raise Http404("Не получилось найти очередь. Скорее всего её уже удалили")
    queue = Queue.objects.get( queue_id = queue_id )
    users = UserInQueue.objects.filter( uiq_queue_id = queue_id).order_by('uiq_index')
    current_user = list(filter(lambda item: item.uiq_user_id == request.user.id, users))
    if len(current_user) == 0:
        return render(request, 'lab_queue/detail.html', {
            'queue': queue, 
            'users': users, 
        })
    else:
        return render(request, 'lab_queue/detail.html', {
            'queue': queue, 
            'users': users, 
            'current_user': current_user[0],
        })

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            first_name = user_form.cleaned_data.get('first_name')
            messages.success(request, f'Аккаунт был создан, удачи постоять в очередях, {first_name}')
            return redirect('/lab_queue/login')
        else:
            messages.error(request, f'Что-то пошло не так, аккаунт не был создан')
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileForm()
    return render(request, 'lab_queue/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    } )

@login_required
def newqueue(request):
    form = NewQueueForm()
    print('test newqueue', form.is_valid())
    
    if request.method == 'POST':
        form = NewQueueForm(request.POST)
        if form.is_valid():
            qwer = form.save()
            print('solid,',qwer)
    return render(request, 'lab_queue/newqueue.html',
    {
        'form' : form
    })

@login_required
def account(request):
    return render(request, 'lab_queue/account.html')