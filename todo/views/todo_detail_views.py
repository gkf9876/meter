from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from ..forms import TodoDetailForm
from ..models import Todo, TodoDetail


@login_required(login_url='common:login')
def tododetail_create(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, use_yn='Y')
    if request.method == 'POST':
        form = TodoDetailForm(request.POST)
        if form.is_valid():
            todo_detail = form.save(commit=False)
            todo_detail.author = request.user
            todo_detail.todo = todo
            todo_detail.create_date = timezone.now()
            todo_detail.save()
            return redirect('todo:detail', todo_id=todo.id)
    else:
        form = TodoDetailForm()
    context = {'todo': todo, 'form': form}
    return render(request, 'todo/detail.html', context)

@login_required(login_url='common:login')
def tododetail_modify(request, todo_detail_id):
    todo_detail = get_object_or_404(TodoDetail, pk=todo_detail_id, use_yn='Y')
    if request.user != todo_detail.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('todo:detail', todo_id=todo_detail.todo.id)
    if request.method == 'POST':
        form = TodoDetailForm(request.POST, instance=todo_detail)
        if form.is_valid():
            todo_detail = form.save(commit=False)
            todo_detail.update_date = timezone.now()
            todo_detail.save()
            return redirect('todo:detail', todo_id=todo_detail.todo.id)
    else:
        form = TodoDetailForm(instance=todo_detail)
    context = {'form': form}
    return render(request, 'todo/detail_form.html', context)

@login_required(login_url='common:login')
def tododetail_delete(request, todo_detail_id):
    todo_detail = get_object_or_404(TodoDetail, pk=todo_detail_id, use_yn='Y')
    if request.user != todo_detail.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('todo:detail', todo_id=todo_detail.todo.id)
    todo_detail.use_yn = 'N'
    todo_detail.update_date = timezone.now()
    todo_detail.save()
    return redirect('todo:detail', todo_id=todo_detail.todo_id)