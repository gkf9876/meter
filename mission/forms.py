from django import forms
from .models import Mission, MissionDetail

class MissionForm(forms.ModelForm):
    notice_yn = forms.BooleanField(required=False, initial=False, label='공지여부')

    class Meta:
        model = Mission
        fields = ['subject', 'content', 'notice_yn']
        labels = {
            'subject': '제목',
            'content': '내용',
            'notice_yn': '공지여부',
        }

class MissionDetailForm(forms.ModelForm):
    class Meta:
        model = MissionDetail
        fields = ['content']
        labels = {
            'content': '실천내용',
        }