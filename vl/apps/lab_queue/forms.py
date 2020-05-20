from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _
from .models import Profile, UserInQueue, Queue
from django.forms import formset_factory

from django.contrib.postgres.fields import ArrayField
from django.db import models



class DateInput(forms.DateInput):
    input_type = 'time'


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name',
                  'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user


TYPE_CHOISES_RU = [
    ('student', 'Студент'),
    ('teacher', 'Преподаватель'),
    ('headman', 'Староста'),
]


class ProfileForm(forms.ModelForm):
    user_type = forms.ChoiceField(
        label=_('Кто я?'),
        required=True,
        choices=TYPE_CHOISES_RU,
    )
    user_group = forms.IntegerField(
        label=_('Группа'),
        help_text=_('В полной форме (85350?)')
    )

    class Meta:
        model = Profile
        fields = ['user_group', 'user_type']


class NewQueueForm(forms.ModelForm):
    queue_enter_date = forms.DateTimeField(
        label='Дата и время открытия очереди', required=False,
        widget=forms.DateTimeInput
    )
    class Meta:
        model = Queue
        fields = ['queue_title', 'queue_group', 'queue_info',
                  'queue_enter_date']

class StatusCheckBoxField(forms.Form):
    status = forms.BooleanField(widget=forms.CheckboxInput(attrs={'onclick':'this.form.submit();'}),required=False, label="")

class PriorityForm(forms.Form):
    priority = forms.CharField(
        required = False, label=''
    )

class PriorityChoiceForm(forms.Form):
    choices = forms.MultipleChoiceField(
            choices=(),
            widget=forms.CheckboxSelectMultiple(
                choices=(),
                attrs={'class':'nobull'},
            ),
            label='Приоритеты',
            required=False
    )

    def __init__(self, choices, *args, **kwargs):
        super(PriorityChoiceForm, self).__init__(*args, **kwargs)
        # label_choices = []
        # for choice in choices: label_choices.append(list(eval(choice))[1])
        self.fields['choices'].choices = choices   
    

class EditQueueForm(forms.ModelForm):
    queue_title = forms.CharField(label='Название очереди', required=True)
    queue_group = forms.IntegerField(label='Целевая группа', required=True)
    queue_info = forms.CharField(
        label='Дополнительная информация', required=False)
    queue_enter_date = forms.DateTimeField(
        label='Дата и время открытия очереди', required=False,
        widget=forms.DateTimeInput
    )

    class Meta:
        model = Queue
        fields = ['queue_title', 'queue_group',
                  'queue_info', 'queue_enter_date']


class EditUserForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        del self.fields['password']

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class QueueEnterForm(forms.ModelForm):
    # additional_info = forms.CharField()
    class Meta:
        model = UserInQueue
        fields = ['uiq_info']


class ChangeQueueIndexForm(forms.Form):
    queue_swap = forms.CharField(required=False)
    queue_move_up = forms.CharField(required=False)
    queue_move_down = forms.CharField(required=False)


class ChangeInfoForm(forms.Form):
    uiq_info = forms.CharField(required=False)


class ConfirmForm(forms.Form):
    queue_delete_start = forms.BooleanField(required=False)
    queue_delete_confirm_true = forms.IntegerField(required=False)
    queue_delete_confirm_false = forms.BooleanField(required=False)
