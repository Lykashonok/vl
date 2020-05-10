from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import Profile, UserInQueue

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(required = True)
    last_name = forms.CharField(required = True)
    
    class Meta:
        model = User
        fields = ['username','first_name','last_name','password1','password2']

    def save(self, commit = True):
        user = super().save(commit = False)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user

TYPE_CHOISES_RU = [
    ('student', 'Студент'),
    ('teacher', 'Преподаватель'),
]
class ProfileForm(forms.ModelForm):
    user_type = forms.ChoiceField(
        # label = _('Кто я?'),
        required = True,
        choices = TYPE_CHOISES_RU,
    )
    user_group = forms.IntegerField(
        # label = _('Группа'),
    )
    class Meta:
        model = Profile
        fields = ['user_group', 'user_type']

class QueueEnterForm(forms.ModelForm):
    # additional_info = forms.CharField()
    class Meta:
        model = UserInQueue
        fields = ['uiq_info']

class OnePropertyForm(forms.Form):
    queue_swap = forms.CharField(required = False)