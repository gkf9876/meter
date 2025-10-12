from django import forms
from .models import ScheduleItem, Schedule, ScheduleDetail

class ScheduleItemForm(forms.ModelForm):
    class Meta:
        model = ScheduleItem
        fields = ['title', 'start_time', 'end_time', 'color', 'use_yn']
        labels = {
            'title': '일정내용',
            'start_time': '시작시간',
            'end_time': '종료시간',
            'color': '색상',
            'use_yn': '사용여부',
        }

class ScheduleForm(forms.ModelForm):
    notice_yn = forms.BooleanField(required=False, initial=False, label='공지여부')

    class Meta:
        model = Schedule
        fields = ['subject', 'content', 'notice_yn']
        labels = {
            'subject': '제목',
            'content': '내용',
            'notice_yn': '공지여부',
        }

class ScheduleDetailForm(forms.ModelForm):
    class Meta:
        model = ScheduleDetail
        fields = ['content']
        labels = {
            'content': '실천내용',
        }