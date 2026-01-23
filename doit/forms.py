from django import forms
from .models import Doit, DoitDetail

class DoitForm(forms.ModelForm):
    notice_yn = forms.BooleanField(required=False, initial=False, label='공지여부')

    class Meta:
        model = Doit
        fields = ['subject', 'content', 'notice_yn']
        labels = {
            'subject': '제목',
            'content': '내용',
            'notice_yn': '공지여부',
        }

class DoitDetailForm(forms.ModelForm):
    class Meta:
        model = DoitDetail
        fields = ['content']
        labels = {
            'content': '실천내용',
        }