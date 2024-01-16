from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from ..forms import TodoForm
from ..models import Todo


@login_required(login_url='common:login')
def todo_create(request):
    if request.method == 'POST':
        check_yn = request.GET.get('check_yn', '')
        form = TodoForm(request.user, request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.author = request.user
            todo.create_date = timezone.now()
            todo.save()
            url = reverse('todo:todo_index') + '?check_yn={}'.format(check_yn)
            return redirect(url)
    else:
        form = TodoForm(request.user)
    check_yn = request.GET.get('check_yn', '')
    context = {'form': form, 'check_yn':check_yn}
    return render(request, 'todo/todo_form.html', context)

@login_required(login_url='common:login')
def todo_modify(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, use_yn='Y')
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
    todo = get_object_or_404(Todo, pk=todo_id, use_yn='Y')
    if request.user != todo.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('todo:todo_detail', todo_id=todo.id)
    todo.use_yn = 'N'
    todo.update_date = timezone.now()
    todo.save()

    children = todo.get_descendants()
    for child in children:
        child.use_yn = 'N'
        child.update_date = timezone.now()
        child.save()

    return redirect('todo:todo_index')

@login_required(login_url='common:login')
def todo_dragdrop(request):
    target_id = request.GET.get('target_id', '')
    id = request.GET.get('id', '')
    check_yn = request.GET.get('check_yn', '')

    target_todo = get_object_or_404(Todo, pk=target_id, use_yn='Y')
    if request.user != target_todo.author:
        messages.error(request, '권한이 없습니다')
        url = reverse('todo:todo_index') + '?check_yn={}'.format(check_yn)
        return redirect(url)

    todo = get_object_or_404(Todo, pk=id, use_yn='Y')
    if request.user != todo.author:
        messages.error(request, '권한이 없습니다')
        url = reverse('todo:todo_index') + '?check_yn={}'.format(check_yn)
        return redirect(url)

    if target_id == id:
        messages.error(request, '드래그 오류')
        url = reverse('todo:todo_index') + '?check_yn={}'.format(check_yn)
        return redirect(url)

    if target_todo.is_descendant_of(todo):
        messages.error(request, '잘못된 위치입니다.')
        url = reverse('todo:todo_index') + '?check_yn={}'.format(check_yn)
        return redirect(url)
    
    todo.parent = target_todo
    todo.save()

    url = reverse('todo:todo_index') + '?check_yn={}'.format(check_yn)
    return redirect(url)

@login_required(login_url='common:login')
def todo_check(request, todo_id, check_yn):
    get_check_yn = request.GET.get('check_yn', '')
    todo = get_object_or_404(Todo, pk=todo_id, use_yn='Y')
    if request.user != todo.author:
        messages.error(request, '권한이 없습니다')
        url = reverse('todo:todo_index') + '?check_yn={}'.format(get_check_yn)
        return redirect(url)
    todo.check_yn = check_yn
    todo.update_date = timezone.now()
    todo.save()

    children = todo.get_descendants()
    for child in children:
        child.check_yn = check_yn
        child.update_date = timezone.now()
        child.save()

    url = reverse('todo:todo_index') + '?check_yn={}'.format(get_check_yn)
    return redirect(url)
