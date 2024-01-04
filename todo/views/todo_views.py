from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from ..forms import TodoForm
from ..models import Todo


@login_required(login_url='common:login')
def todo_create(request):
    if request.method == 'POST':
        form = TodoForm(request.user, request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.author = request.user
            todo.create_date = timezone.now()
            todo.save()
            return redirect('todo:todo_index')
    else:
        form = TodoForm(request.user)
    context = {'form': form}
    return render(request, 'todo/todo_form.html', context)

@login_required(login_url='common:login')
def todo_modify(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id)
    if request.user != todo.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('todo:todo_detail', todo_id=todo.id)
    if request.method == 'POST':
        form = TodoForm(request.user, request.POST, instance=todo)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.update_date = timezone.now()
            todo.save()
            return redirect('todo:todo_detail', todo_id=todo.id)
    else:
        form = TodoForm(request.user, instance=todo)
    context = {'form': form}
    return render(request, 'todo/todo_form.html', context)

@login_required(login_url='common:login')
def todo_delete(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id)
    if request.user != todo.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('todo:todo_detail', todo_id=todo.id)
    todo.delete()
    return redirect('todo:todo_index')