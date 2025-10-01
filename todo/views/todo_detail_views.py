import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone

from common.models import File
from ..forms import TodoDetailForm
from ..models import Todo, TodoDetail
from datetime import datetime


@login_required(login_url='common:login')
def tododetail_create(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, use_yn='Y')
    if request.method == 'POST':
        form = TodoDetailForm(request.POST)
        if form.is_valid():
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d')
                context = {'todo': todo, 'form': form, 'date': date}
                return render(request, 'todo/detail.html', context)
            todo_detail = form.save(commit=False)
            todo_detail.author = request.user
            todo_detail.todo = todo
            todo_detail.create_date = timezone.now()
            todo_detail.save()
            files = request.FILES.getlist('file')
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                todo_detail.file.add(file_instance)
            return redirect('{}#tododetail_{}'.format(resolve_url('todo:detail', todo_id=todo.id), todo_detail.id))
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
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d')
                context = {'form': form, 'date':date}
                return render(request, 'todo/detail_form.html', context)
            todo_detail = form.save(commit=False)
            todo_detail.update_date = timezone.now()
            todo_detail.save()
            files = request.FILES.getlist('file')
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                todo_detail.file.add(file_instance)
            delete_file_id_list = request.POST.getlist('delete_attached_file')
            for file_id in delete_file_id_list:
                file = todo_detail.file.get(pk=file_id)
                todo_detail.file.remove(file.id)
                file_path = file.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            return redirect('{}#tododetail_{}'.format(resolve_url('todo:detail', todo_id=todo_detail.todo.id), todo_detail.id))
    else:
        form = TodoDetailForm(instance=todo_detail)
    context = {'form': form, 'date':todo_detail.date}
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