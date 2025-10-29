import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone

from common.views import move_temp_images_to_uploads
from common.models import File
from .forms import MissionForm, MissionDetailForm
from .models import Mission, MissionDetail


@login_required(login_url='common:login')
def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    mission_list = Mission.objects.filter(Q(author_id=request.user.id) | Q(notice_yn=True), use_yn='Y').order_by('-notice_yn', '-create_date')
    if kw:
        mission_list = mission_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(missiondetail__content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(missiondetail__author__username__icontains=kw)
        ).distinct()
    paginator = Paginator(mission_list, 10)
    page_obj = paginator.get_page(page)
    context = {'mission_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'mission/list.html', context)

@login_required(login_url='common:login')
def detail(request, mission_id):
    mission = get_object_or_404(Mission, Q(author_id=request.user.id) | Q(notice_yn=True), pk=mission_id, use_yn='Y')
    if request.user != mission.author:
        mission.viewcount.add(request.user)
    context = {'mission': mission}
    return render(request, 'mission/detail.html', context)

@login_required(login_url='common:login')
def create(request):
    if request.method == 'POST':
        form = MissionForm(request.POST)
        if form.is_valid():
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'mission/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'mission/form.html', context)
            mission = form.save(commit=False)
            mission.author = request.user
            mission.create_date = timezone.now()
            mission.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                mission.file.add(file_instance)
            return redirect('mission:index')
    else:
        form = MissionForm()
    context = {'form': form}
    return render(request, 'mission/form.html', context)

@login_required(login_url='common:login')
def modify(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    if request.user != mission.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('mission:detail', mission_id=mission.id)
    if request.method == "POST":
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            files = request.FILES.getlist('file')
            delete_file_id_list = request.POST.getlist('delete_attached_file')
            total_files_size = sum([file.size for file in files])
            total_files_size += sum([file.file.size for file in mission.file.all() if str(file.id) not in delete_file_id_list])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'mission/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'mission/form.html', context)
            mission = form.save(commit=False)
            mission.update_date = timezone.now()
            mission.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                mission.file.add(file_instance)
            for file_id in delete_file_id_list:
                file = mission.file.get(pk=file_id)
                mission.file.remove(file.id)
                file_path = file.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            return redirect('mission:detail', mission_id=mission.id)
    else:
        form = MissionForm(instance=mission)
    context = {'form': form}
    return render(request, 'mission/form.html', context)

@login_required(login_url='common:login')
def delete(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    if request.user != mission.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('mission:detail', mission_id=mission.id)
    mission.modify_date = timezone.now()
    mission.use_yn = 'N'
    mission.save()
    return redirect('mission:index')

@login_required(login_url='common:login')
def detail_create(request, mission_id):
    """
    실천내용 등록
    """
    mission = get_object_or_404(Mission, pk=mission_id)
    if request.method == "POST":
        form = MissionDetailForm(request.POST)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'mission': mission, 'form': form}
                return render(request, 'mission/detail.html', context)
            missiondetail = form.save(commit=False)
            missiondetail.author = request.user
            missiondetail.create_date = timezone.now()
            missiondetail.mission = mission
            missiondetail.save()
            return redirect('{}#missiondetail_{}'.format(resolve_url('mission:detail', mission_id=mission.id), missiondetail.id))
    else:
        form = MissionDetailForm()
    context = {'mission': mission, 'form': form}
    return render(request, 'mission/detail.html', context)


@login_required(login_url='common:login')
def detail_modify(request, missiondetail_id):
    missiondetail = get_object_or_404(MissionDetail, pk=missiondetail_id)
    if request.user != missiondetail.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('mission:detail', mission_id=missiondetail.mission.id)
    if request.method == "POST":
        form = MissionDetailForm(request.POST, instance=missiondetail)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'missiondetail':missiondetail, 'form': form}
                return render(request, 'mission/detail_form.html', context)
            missiondetail = form.save(commit=False)
            missiondetail.update_date = timezone.now()
            missiondetail.save()
            return redirect('{}#missiondetail_{}'.format(resolve_url('mission:detail', mission_id=missiondetail.mission.id), missiondetail.id))
    else:
        form = MissionDetailForm(instance=missiondetail)
    context = {'missiondetail':missiondetail, 'form': form}
    return render(request, 'mission/detail_form.html', context)

@login_required(login_url='common:login')
def detail_delete(request, missiondetail_id):
    missiondetail = get_object_or_404(MissionDetail, pk=missiondetail_id)
    if request.user != missiondetail.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        missiondetail.update_date = timezone.now()
        missiondetail.use_yn = 'N'
        missiondetail.save()
    return redirect('mission:detail', mission_id=missiondetail.mission.id)

@login_required(login_url='common:login')
def vote(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    if request.user == mission.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        mission.voter.add(request.user)
    return redirect('mission:detail', mission_id=mission.id)

@login_required(login_url='common:login')
def detail_vote(request, missiondetail_id):
    missiondetail = get_object_or_404(MissionDetail, pk=missiondetail_id)
    if request.user == missiondetail.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        missiondetail.voter.add(request.user)
    return redirect('mission:detail', mission_id=missiondetail.mission.id)