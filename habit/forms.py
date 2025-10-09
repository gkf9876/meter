from django import forms
from .models import Habit, HabitDetail

class HabitForm(forms.ModelForm):
    notice_yn = forms.BooleanField(required=False, initial='N', label='공지여부')

    class Meta:
        model = Habit
        fields = ['subject', 'content', 'notice_yn']
        labels = {
            'subject': '제목',
            'content': '내용',
            'notice_yn': '공지여부',
        }

class HabitDetailForm(forms.ModelForm):
    class Meta:
        model = HabitDetail
        fields = ['content']
        labels = {
            'content': '실천내용',
        }