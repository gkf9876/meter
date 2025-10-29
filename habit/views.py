import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone

from common.models import File
from common.views import move_temp_images_to_uploads, delete_unused_images
from .forms import HabitForm, HabitDetailForm
from .models import Habit, HabitDetail


@login_required(login_url='common:login')
def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    habit_list = Habit.objects.filter(Q(author_id=request.user.id) | Q(notice_yn=True), use_yn='Y').order_by('-notice_yn', '-create_date')
    if kw:
        habit_list = habit_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(habitdetail__content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(habitdetail__author__username__icontains=kw)
        ).distinct()
    paginator = Paginator(habit_list, 10)
    page_obj = paginator.get_page(page)
    context = {'habit_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'habit/list.html', context)

@login_required(login_url='common:login')
def detail(request, habit_id):
    habit = get_object_or_404(Habit, Q(author_id=request.user.id) | Q(notice_yn=True), pk=habit_id, use_yn='Y')
    if request.user != habit.author:
        habit.viewcount.add(request.user)
    context = {'habit': habit}
    return render(request, 'habit/detail.html', context)

@login_required(login_url='common:login')
def create(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'habit/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'habit/form.html', context)
            habit = form.save(commit=False)
            habit.author = request.user
            habit.create_date = timezone.now()
            habit.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                habit.file.add(file_instance)
            return redirect('habit:index')
    else:
        form = HabitForm()
    context = {'form': form}
    return render(request, 'habit/form.html', context)

@login_required(login_url='common:login')
def modify(request, habit_id):
    habit = get_object_or_404(Habit, pk=habit_id)
    if request.user != habit.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('habit:detail', habit_id=habit.id)
    if request.method == "POST":
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            files = request.FILES.getlist('file')
            delete_file_id_list = request.POST.getlist('delete_attached_file')
            total_files_size = sum([file.size for file in files])
            total_files_size += sum([file.file.size for file in habit.file.all() if str(file.id) not in delete_file_id_list])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'habit/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'habit/form.html', context)
            delete_unused_images(habit.content, request.POST.get('content', ''))
            habit = form.save(commit=False)
            habit.update_date = timezone.now()
            habit.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                habit.file.add(file_instance)
            for file_id in delete_file_id_list:
                file = habit.file.get(pk=file_id)
                habit.file.remove(file.id)
                file_path = file.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            return redirect('habit:detail', habit_id=habit.id)
    else:
        form = HabitForm(instance=habit)
    context = {'form': form}
    return render(request, 'habit/form.html', context)

@login_required(login_url='common:login')
def delete(request, habit_id):
    habit = get_object_or_404(Habit, pk=habit_id)
    if request.user != habit.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('habit:detail', habit_id=habit.id)
    habit.modify_date = timezone.now()
    habit.use_yn = 'N'
    habit.save()
    return redirect('habit:index')

@login_required(login_url='common:login')
def detail_create(request, habit_id):
    """
    실천내용 등록
    """
    habit = get_object_or_404(Habit, pk=habit_id)
    if request.method == "POST":
        form = HabitDetailForm(request.POST)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'habit': habit, 'form': form}
                return render(request, 'habit/detail.html', context)
            habitdetail = form.save(commit=False)
            habitdetail.author = request.user
            habitdetail.create_date = timezone.now()
            habitdetail.habit = habit
            habitdetail.save()
            return redirect('{}#habitdetail_{}'.format(resolve_url('habit:detail', habit_id=habit.id), habitdetail.id))
    else:
        form = HabitDetailForm()
    context = {'habit': habit, 'form': form}
    return render(request, 'habit/detail.html', context)


@login_required(login_url='common:login')
def detail_modify(request, habitdetail_id):
    habitdetail = get_object_or_404(HabitDetail, pk=habitdetail_id)
    habitdetail_content = habitdetail.content
    if request.user != habitdetail.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('habit:detail', habit_id=habitdetail.habit.id)
    if request.method == "POST":
        form = HabitDetailForm(request.POST, instance=habitdetail)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'habitdetail':habitdetail, 'form': form}
                return render(request, 'habit/detail_form.html', context)
            delete_unused_images(habitdetail_content, request.POST.get('content', ''))
            habitdetail = form.save(commit=False)
            habitdetail.update_date = timezone.now()
            habitdetail.save()
            return redirect('{}#habitdetail_{}'.format(resolve_url('habit:detail', habit_id=habitdetail.habit.id), habitdetail.id))
    else:
        form = HabitDetailForm(instance=habitdetail)
    context = {'habitdetail':habitdetail, 'form': form}
    return render(request, 'habit/detail_form.html', context)

@login_required(login_url='common:login')
def detail_delete(request, habitdetail_id):
    habitdetail = get_object_or_404(HabitDetail, pk=habitdetail_id)
    if request.user != habitdetail.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        habitdetail.update_date = timezone.now()
        habitdetail.use_yn = 'N'
        habitdetail.save()
    return redirect('habit:detail', habit_id=habitdetail.habit.id)

@login_required(login_url='common:login')
def vote(request, habit_id):
    habit = get_object_or_404(Habit, pk=habit_id)
    if request.user == habit.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        habit.voter.add(request.user)
    return redirect('habit:detail', habit_id=habit.id)

@login_required(login_url='common:login')
def detail_vote(request, habitdetail_id):
    habitdetail = get_object_or_404(HabitDetail, pk=habitdetail_id)
    if request.user == habitdetail.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        habitdetail.voter.add(request.user)
    return redirect('habit:detail', habit_id=habitdetail.habit.id)