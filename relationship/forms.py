from django import forms
from .models import Relationship, RelationshipDetail

class RelationshipForm(forms.ModelForm):
    notice_yn = forms.BooleanField(required=False, initial=False, label='공지여부')

    class Meta:
        model = Relationship
        fields = ['subject', 'content', 'notice_yn']
        labels = {
            'subject': '제목',
            'content': '내용',
            'notice_yn': '공지여부',
        }

class RelationshipDetailForm(forms.ModelForm):
    class Meta:
        model = RelationshipDetail
        fields = ['content']
        labels = {
            'content': '실천내용',
        }