from django import forms
from .models import Diary, DiaryDetail

class DiaryForm(forms.ModelForm):
    notice_yn = forms.BooleanField(required=False, initial=False, label='공지여부')

    class Meta:
        model = Diary
        fields = ['subject', 'content', 'notice_yn']
        labels = {
            'subject': '제목',
            'content': '내용',
            'notice_yn': '공지여부',
        }

class DiaryDetailForm(forms.ModelForm):
    class Meta:
        model = DiaryDetail
        fields = ['content']
        labels = {
            'content': '실천내용',
        }