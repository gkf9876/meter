import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone

from common.models import File
from common.views import move_temp_images_to_uploads, delete_unused_images
from .forms import HealthForm, HealthDetailForm
from .models import Health, HealthDetail


@login_required(login_url='common:login')
@permission_required('health.view_health', raise_exception=False)
def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    health_list = Health.objects.filter(Q(author_id=request.user.id) | Q(notice_yn=True), use_yn='Y').order_by('-notice_yn', '-create_date')
    if kw:
        health_list = health_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(healthdetail__content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(healthdetail__author__username__icontains=kw)
        ).distinct()
    paginator = Paginator(health_list, 10)
    page_obj = paginator.get_page(page)
    context = {'health_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'health/list.html', context)

@login_required(login_url='common:login')
@permission_required('health.view_health', raise_exception=False)
def detail(request, health_id):
    health = get_object_or_404(Health, Q(author_id=request.user.id) | Q(notice_yn=True), pk=health_id, use_yn='Y')
    if request.user != health.author:
        health.viewcount.add(request.user)
    context = {'health': health}
    return render(request, 'health/detail.html', context)

@login_required(login_url='common:login')
@permission_required('health.add_health', raise_exception=False)
def create(request):
    if request.method == 'POST':
        form = HealthForm(request.POST)
        if form.is_valid():
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'health/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'health/form.html', context)
            health = form.save(commit=False)
            health.author = request.user
            health.create_date = timezone.now()
            health.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                health.file.add(file_instance)
            return redirect('health:index')
    else:
        form = HealthForm()
    context = {'form': form}
    return render(request, 'health/form.html', context)

@login_required(login_url='common:login')
@permission_required('health.change_health', raise_exception=False)
def modify(request, health_id):
    health = get_object_or_404(Health, pk=health_id)
    if request.user != health.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('health:detail', health_id=health.id)
    if request.method == "POST":
        form = HealthForm(request.POST, instance=health)
        if form.is_valid():
            files = request.FILES.getlist('file')
            delete_file_id_list = request.POST.getlist('delete_attached_file')
            total_files_size = sum([file.size for file in files])
            total_files_size += sum([file.file.size for file in health.file.all() if str(file.id) not in delete_file_id_list])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'health/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'health/form.html', context)
            delete_unused_images(health.content, request.POST.get('content', ''))
            health = form.save(commit=False)
            health.update_date = timezone.now()
            health.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                health.file.add(file_instance)
            for file_id in delete_file_id_list:
                file = health.file.get(pk=file_id)
                health.file.remove(file.id)
                file_path = file.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            return redirect('health:detail', health_id=health.id)
    else:
        form = HealthForm(instance=health)
    context = {'form': form}
    return render(request, 'health/form.html', context)

@login_required(login_url='common:login')
@permission_required('health.delete_health', raise_exception=False)
def delete(request, health_id):
    health = get_object_or_404(Health, pk=health_id)
    if request.user != health.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('health:detail', health_id=health.id)
    health.modify_date = timezone.now()
    health.use_yn = 'N'
    health.save()
    return redirect('health:index')

@login_required(login_url='common:login')
@permission_required('health.add_healthdetail', raise_exception=False)
def detail_create(request, health_id):
    """
    실천내용 등록
    """
    health = get_object_or_404(Health, pk=health_id)
    if request.method == "POST":
        form = HealthDetailForm(request.POST)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'health': health, 'form': form}
                return render(request, 'health/detail.html', context)
            healthdetail = form.save(commit=False)
            healthdetail.author = request.user
            healthdetail.create_date = timezone.now()
            healthdetail.health = health
            healthdetail.save()
            return redirect('{}#healthdetail_{}'.format(resolve_url('health:detail', health_id=health.id), healthdetail.id))
    else:
        form = HealthDetailForm()
    context = {'health': health, 'form': form}
    return render(request, 'health/detail.html', context)


@login_required(login_url='common:login')
@permission_required('health.change_healthdetail', raise_exception=False)
def detail_modify(request, healthdetail_id):
    healthdetail = get_object_or_404(HealthDetail, pk=healthdetail_id)
    healthdetail_content = healthdetail.content
    if request.user != healthdetail.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('health:detail', health_id=healthdetail.health.id)
    if request.method == "POST":
        form = HealthDetailForm(request.POST, instance=healthdetail)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'healthdetail':healthdetail, 'form': form}
                return render(request, 'health/detail_form.html', context)
            delete_unused_images(healthdetail_content, request.POST.get('content', ''))
            healthdetail = form.save(commit=False)
            healthdetail.update_date = timezone.now()
            healthdetail.save()
            return redirect('{}#healthdetail_{}'.format(resolve_url('health:detail', health_id=healthdetail.health.id), healthdetail.id))
    else:
        form = HealthDetailForm(instance=healthdetail)
    context = {'healthdetail':healthdetail, 'form': form}
    return render(request, 'health/detail_form.html', context)

@login_required(login_url='common:login')
@permission_required('health.delete_healthdetail', raise_exception=False)
def detail_delete(request, healthdetail_id):
    healthdetail = get_object_or_404(HealthDetail, pk=healthdetail_id)
    if request.user != healthdetail.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        healthdetail.update_date = timezone.now()
        healthdetail.use_yn = 'N'
        healthdetail.save()
    return redirect('health:detail', health_id=healthdetail.health.id)

@login_required(login_url='common:login')
@permission_required('health.view_health', raise_exception=False)
def vote(request, health_id):
    health = get_object_or_404(Health, pk=health_id)
    if request.user == health.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        health.voter.add(request.user)
    return redirect('health:detail', health_id=health.id)

@login_required(login_url='common:login')
@permission_required('health.view_healthdetail', raise_exception=False)
def detail_vote(request, healthdetail_id):
    healthdetail = get_object_or_404(HealthDetail, pk=healthdetail_id)
    if request.user == healthdetail.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        healthdetail.voter.add(request.user)
    return redirect('health:detail', health_id=healthdetail.health.id)