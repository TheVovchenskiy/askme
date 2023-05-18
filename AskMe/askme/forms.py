from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from askme import models


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)
    password_check = forms.CharField(min_length=8, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'username']

    def save(self):
        self.cleaned_data.pop('password_check')
        return User.objects.create_user(**self.cleaned_data)

    def clean_password_check(self):
        password = self.cleaned_data['password']
        password_check = self.cleaned_data['password_check']
        if password != password_check:
            raise forms.ValidationError("Passwords do not match")


class SettingsForm(UserChangeForm):
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['email', 'username']

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.fields.pop('password')
        # self.fields['avatar'].initial = self.instance.profile.avatar


class AddQuestionForm(forms.ModelForm):
    tags = forms.CharField(
        help_text='Add tags for your question, separated by space'
    )

    class Meta:
        model = models.Question
        fields = ['title', 'content']
