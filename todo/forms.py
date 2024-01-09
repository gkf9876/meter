from django import forms
from mptt.forms import TreeNodeChoiceField
from todo.models import Todo, TodoDetail
from tinymce.widgets import TinyMCE

class TodoForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=None, required=False)

    class Meta:
        model = Todo
        fields = ['parent', 'subject']
        labels = {
            'parent': '상위값',
            'subject': '할일',
        }

    def __init__(self, user, *args, **kwargs):
        super(TodoForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = Todo.objects.filter(author_id=user.id)

class TodoDetailForm(forms.ModelForm):
    class Meta:
        model = TodoDetail
        fields = ['date', 'content']
        labels = {
            'date': '날짜',
            'content': '내용',
        }
        widgets = {
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30}),
        }