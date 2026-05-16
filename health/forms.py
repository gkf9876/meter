from django import forms
from .models import Health, HealthDetail

class HealthForm(forms.ModelForm):
    notice_yn = forms.BooleanField(required=False, initial=False, label='공지여부')

    class Meta:
        model = Health
        fields = ['subject', 'content', 'notice_yn']
        labels = {
            'subject': '제목',
            'content': '내용',
            'notice_yn': '공지여부',
        }

class HealthDetailForm(forms.ModelForm):
    class Meta:
        model = HealthDetail
        fields = ['content']
        labels = {
            'content': '실천내용',
        }