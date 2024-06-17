from django import forms
from django.contrib.auth.models import User

from .models import Client, ClientUser


class ClientForm(forms.ModelForm):
    username = forms.CharField(label='Username')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = Client
        fields = ['username', 'first_name', 'last_name', 'email', 'contact_phone', 'company', 'domains', 'lms_url', 'lms_api_key',
                  'lms_api_secret', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("The two password fields didn’t match.")

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email


class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["first_name", "last_name", "email", "contact_phone", "company", "domains", "lms_url", "lms_api_key",
                  "lms_api_secret"]

    def __init__(self, *args, **kwargs):
        super(ClientUpdateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = False
        self.fields['contact_phone'].required = False
        self.fields['company'].required = False
        self.fields['domains'].required = False
        self.fields['lms_url'].required = False
        self.fields['lms_api_key'].required = False
        self.fields['lms_api_secret'].required = False

    def save(self, commit=True):
        client = super().save(commit=False)
        user = client.user
        if self.cleaned_data["first_name"]:
            user.first_name = self.cleaned_data["first_name"]
        else:
            user.first_name = ""
        if self.cleaned_data["last_name"]:
            user.last_name = self.cleaned_data["last_name"]
        else:
            user.last_name = ""

        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            client.save()
        return client


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = ClientUser
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = False
