import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone

from common.models import File
from .forms import ScheduleForm, ScheduleDetailForm, ScheduleItemForm
from .models import Schedule, ScheduleDetail, ScheduleItem

@login_required(login_url='common:login')
def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    schedule_list = Schedule.objects.filter(Q(author_id=request.user.id) | Q(notice_yn=True), use_yn='Y').order_by('-notice_yn', '-create_date')
    if kw:
        schedule_list = schedule_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(scheduledetail__content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(scheduledetail__author__username__icontains=kw)
        ).distinct()
    paginator = Paginator(schedule_list, 10)
    page_obj = paginator.get_page(page)
    context = {'schedule_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'schedule/list.html', context)

@login_required(login_url='common:login')
def detail(request, schedule_id):
    schedule = get_object_or_404(Schedule, Q(author_id=request.user.id) | Q(notice_yn=True), pk=schedule_id, use_yn='Y')

    schedule_item = schedule.schedule_item.filter(use_yn='Y').order_by('start_time', 'end_time')

    labels = []
    values = []
    colors = []
    for s in schedule_item:
        labels.append(f"{s.title}")
        values.append(s.duration_minutes())
        colors.append(s.color)

    context = {'schedule': schedule,'labels':labels,'values':values, 'colors':colors}
    return render(request, 'schedule/detail.html', context)

@login_required(login_url='common:login')
def create(request):
    ScheduleFormSet = modelformset_factory(ScheduleItem, form=ScheduleItemForm, extra=0, can_delete=True)

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        formset = ScheduleFormSet(request.POST, queryset=ScheduleItem.objects.none())
        if form.is_valid() and formset.is_valid():
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form, 'formset': formset}
                return render(request, 'schedule/form.html', context)
            schedule = form.save(commit=False)
            schedule.author = request.user
            schedule.create_date = timezone.now()
            schedule.save()
            schedule_items = formset.save(commit=False)
            for item in schedule_items:
                item.save()
                schedule.schedule_item.add(item)
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                schedule.file.add(file_instance)

            # formset.save()
            return redirect('schedule:index')
    else:
        form = ScheduleForm()
        formset = ScheduleFormSet(queryset=ScheduleItem.objects.none())

    context = {'form': form, 'formset': formset}
    return render(request, 'schedule/form.html', context)

@login_required(login_url='common:login')
def modify(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    ScheduleFormSet = modelformset_factory(ScheduleItem, form=ScheduleItemForm, extra=0, can_delete=True)
    if request.user != schedule.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('schedule:detail', schedule_id=schedule.id)
    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule)
        formset = ScheduleFormSet(request.POST, queryset=schedule.schedule_item.filter(use_yn='Y').order_by('start_time', 'end_time'))
        if form.is_valid() and formset.is_valid():
            files = request.FILES.getlist('file')
            delete_file_id_list = request.POST.getlist('delete_attached_file')
            total_files_size = sum([file.size for file in files])
            total_files_size += sum([file.file.size for file in schedule.file.all() if str(file.id) not in delete_file_id_list])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form, 'formset': formset}
                return render(request, 'schedule/form.html', context)
            schedule = form.save(commit=False)
            schedule.update_date = timezone.now()
            schedule.save()
            schedule_items = formset.save(commit=False)
            for item in schedule_items:
                item.save()
                schedule.schedule_item.add(item)
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                schedule.file.add(file_instance)
            for file_id in delete_file_id_list:
                file = schedule.file.get(pk=file_id)
                schedule.file.remove(file.id)
                file_path = file.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            return redirect('schedule:detail', schedule_id=schedule.id)
    else:
        form = ScheduleForm(instance=schedule)
        formset = ScheduleFormSet(queryset=schedule.schedule_item.filter(use_yn='Y').order_by('start_time', 'end_time'))
    context = {'form': form, 'formset': formset}
    return render(request, 'schedule/form.html', context)

@login_required(login_url='common:login')
def delete(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    if request.user != schedule.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('schedule:detail', schedule_id=schedule.id)
    schedule.modify_date = timezone.now()
    schedule.use_yn = 'N'
    schedule.save()
    return redirect('schedule:index')

@login_required(login_url='common:login')
def detail_create(request, schedule_id):
    """
    실천내용 등록
    """
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    if request.method == "POST":
        form = ScheduleDetailForm(request.POST)
        if form.is_valid():
            scheduledetail = form.save(commit=False)
            scheduledetail.author = request.user
            scheduledetail.create_date = timezone.now()
            scheduledetail.schedule = schedule
            scheduledetail.save()
            return redirect('{}#scheduledetail_{}'.format(resolve_url('schedule:detail', schedule_id=schedule.id), scheduledetail.id))
    else:
        form = ScheduleDetailForm()
    context = {'schedule': schedule, 'form': form}
    return render(request, 'schedule/detail.html', context)


@login_required(login_url='common:login')
def detail_modify(request, scheduledetail_id):
    scheduledetail = get_object_or_404(ScheduleDetail, pk=scheduledetail_id)
    if request.user != scheduledetail.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('schedule:detail', schedule_id=scheduledetail.schedule.id)
    if request.method == "POST":
        form = ScheduleDetailForm(request.POST, instance=scheduledetail)
        if form.is_valid():
            scheduledetail = form.save(commit=False)
            scheduledetail.update_date = timezone.now()
            scheduledetail.save()
            return redirect('{}#scheduledetail_{}'.format(resolve_url('schedule:detail', schedule_id=scheduledetail.schedule.id), scheduledetail.id))
    else:
        form = ScheduleDetailForm(instance=scheduledetail)
    context = {'scheduledetail':scheduledetail, 'form': form}
    return render(request, 'schedule/detail_form.html', context)

@login_required(login_url='common:login')
def detail_delete(request, scheduledetail_id):
    scheduledetail = get_object_or_404(ScheduleDetail, pk=scheduledetail_id)
    if request.user != scheduledetail.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        scheduledetail.update_date = timezone.now()
        scheduledetail.use_yn = 'N'
        scheduledetail.save()
    return redirect('schedule:detail', schedule_id=scheduledetail.schedule.id)