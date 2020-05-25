from django import forms
from django.forms import ModelForm
from .models import Profile, Message


class RegisterForm(forms.Form):
    username = forms.CharField(label=u"Имя пользователя")
    first_name = forms.CharField(label=u"Имя")
    last_name = forms.CharField(label=u"Фамилия")
    email = forms.EmailField(label=u"Email", required=False)
    password = forms.CharField(label=u"Пароль", widget=forms.PasswordInput)
    password_confirm = forms.CharField(label=u"Подтвердите пароль", widget=forms.PasswordInput)

    def is_valid(self):
        valid = super(RegisterForm, self).is_valid()
        if self.cleaned_data['password'] != self.cleaned_data['password_confirm']:
            self.add_error("password_confirm", u"Пароли не совпадают")
            return False
        return valid


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        exclude = ['user']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['message']
        labels = {'message': ""}


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100,
                              widget=forms.TextInput(
                                  attrs={'size': '40',
                                         'class': 'form-control'}))
    sender = forms.EmailField(
        widget=forms.TextInput(attrs={'size': '40', 'class': 'form-control'}))
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}))
    copy = forms.BooleanField(required=False)
