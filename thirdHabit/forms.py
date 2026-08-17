from django import forms
from .models import ThirdHabit, ThirdHabitItem, ThirdHabitDetail, ThirdHabitItemDetail, ThirdHabitItemDetailTime


class ThirdHabitForm(forms.ModelForm):
    notice_yn = forms.BooleanField(required=False, initial=False, label='공지여부')

    class Meta:
        model = ThirdHabit
        fields = ['start_date', 'subject', 'content', 'notice_yn']
        labels = {
            'start_date': '시작날짜',
            'subject': '제목',
            'content': '내용',
            'notice_yn': '공지여부',
        }

class ThirdHabitItemForm(forms.ModelForm):
    class Meta:
        model = ThirdHabitItem
        fields = ['content', 'use_yn']
        labels = {
            'content': '내용',
            'use_yn': '사용여부',
        }

class ThirdHabitItemDetailForm(forms.ModelForm):
    class Meta:
        model = ThirdHabitItemDetail
        fields = ['content', 'use_yn']
        labels = {
            'content': '내용',
            'use_yn': '사용여부',
        }

class ThirdHabitItemDetailTimeForm(forms.ModelForm):
    class Meta:
        model = ThirdHabitItemDetailTime
        fields = ['start_day', 'start_time', 'end_day', 'end_time', 'use_yn']
        labels = {
            'start_day': '시작요일',
            'start_time': '시작시간',
            'end_day': '종료요일',
            'end_time': '종료시간',
            'use_yn': '사용여부',
        }

class ThirdHabitDetailForm(forms.ModelForm):
    class Meta:
        model = ThirdHabitDetail
        fields = ['content']
        labels = {
            'content': '내용',
        }