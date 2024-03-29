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
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['email', 'username']

    def save(self, commit=True):
        self.cleaned_data.pop('password_check')
        avatar = self.cleaned_data.pop('avatar')
        user = User.objects.create_user(**self.cleaned_data)
        profile = models.Profile(user=user)
        if avatar:
            profile.avatar = avatar
        profile.save()
        
        return user

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
    
    def save(self, commit=True):
        user = super().save(commit)
        profile = user.profile
        profile.avatar = self.cleaned_data['avatar']
        profile.save()

        return user


class AddQuestionForm(forms.ModelForm):
    tags = forms.CharField(
        help_text='Add tags for your question, separated by space'
    )

    class Meta:
        model = models.Question
        fields = ['title', 'content']


class AddAnswerForm(forms.ModelForm):

    class Meta:
        model = models.Answer
        fields = ['content']
        labels = {
            'content': "Your answer"
        }
        help_texts = {
            'content': 'Answer to this question'
        }
    