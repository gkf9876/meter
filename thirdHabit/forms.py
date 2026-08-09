from django import forms
from .models import ThirdHabit, ThirdHabitItem, ThirdHabitDetail


class ThirdHabitItemForm(forms.ModelForm):
    class Meta:
        model = ThirdHabitItem
        fields = ['content', 'use_yn']
        labels = {
            'content': '내용',
            'use_yn': '사용여부',
        }

class ThirdHabitForm(forms.ModelForm):
    notice_yn = forms.BooleanField(required=False, initial=False, label='공지여부')

    class Meta:
        model = ThirdHabit
        fields = ['subject', 'content', 'notice_yn']
        labels = {
            'subject': '제목',
            'content': '내용',
            'notice_yn': '공지여부',
        }

class ThirdHabitDetailForm(forms.ModelForm):
    class Meta:
        model = ThirdHabitDetail
        fields = ['content']
        labels = {
            'content': '내용',
        }