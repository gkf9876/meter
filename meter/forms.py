from django import forms

from .models import Study


class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['name', 'type']
        labels = {
            'name': '이름',
            'type': '종류',
        }
