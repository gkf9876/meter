from django import forms
from .models import Habit, HabitDetail

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['subject', 'content']
        labels = {
            'subject': '제목',
            'content': '내용',
        }

class HabitDetailForm(forms.ModelForm):
    class Meta:
        model = HabitDetail
        fields = ['content']
        labels = {
            'content': '실천내용',
        }