from django import forms
from .models import Community, CommunityDetail

class CommunityForm(forms.ModelForm):
    notice_yn = forms.BooleanField(required=False, initial=False, label='공지여부')

    class Meta:
        model = Community
        fields = ['subject', 'content', 'notice_yn']
        labels = {
            'subject': '제목',
            'content': '내용',
            'notice_yn': '공지여부',
        }

class CommunityDetailForm(forms.ModelForm):
    class Meta:
        model = CommunityDetail
        fields = ['content']
        labels = {
            'content': '실천내용',
        }