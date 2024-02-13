from django import forms
from memorization.models import Memorization

class MemorizationForm(forms.ModelForm):
    class Meta:
        model = Memorization
        fields = ['subject', 'content']
        labels = {
            'subject': '제목',
            'content': '내용',
        }