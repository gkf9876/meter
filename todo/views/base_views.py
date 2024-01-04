from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from ..models import Todo


@login_required(login_url='common:login')
def index(request):
    context = {'todo_tree': Todo.objects.filter(author_id=request.user.id)}
    return render(request, 'todo/todo_list.html', context)

@login_required(login_url='common:login')
def detail(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id)
    context = {'todo': todo}
    return render(request, 'todo/todo_detail.html', context)