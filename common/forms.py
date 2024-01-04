from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserForm(UserCreationForm):
    email = forms.EmailField(label="이메일")

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email")
        
class FileForm(forms.ModelForm):
    class Meta:
        fields = ['path', 'name']
        labels = {
            'path': '경로',
            'name': '파일명',
        }