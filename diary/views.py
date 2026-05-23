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
from .forms import DiaryForm, DiaryDetailForm
from .models import Diary, DiaryDetail


@login_required(login_url='common:login')
def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    diary_list = Diary.objects.filter(Q(author_id=request.user.id) | Q(notice_yn=True), use_yn='Y').order_by('-notice_yn', '-create_date')
    if kw:
        diary_list = diary_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(diarydetail__content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(diarydetail__author__username__icontains=kw)
        ).distinct()
    paginator = Paginator(diary_list, 10)
    page_obj = paginator.get_page(page)
    context = {'diary_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'diary/list.html', context)

@login_required(login_url='common:login')
def detail(request, diary_id):
    diary = get_object_or_404(Diary, Q(author_id=request.user.id) | Q(notice_yn=True), pk=diary_id, use_yn='Y')
    if request.user != diary.author:
        diary.viewcount.add(request.user)
    context = {'diary': diary}
    return render(request, 'diary/detail.html', context)

@login_required(login_url='common:login')
def create(request):
    if request.method == 'POST':
        form = DiaryForm(request.POST)
        if form.is_valid():
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'diary/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'diary/form.html', context)
            diary = form.save(commit=False)
            diary.author = request.user
            diary.create_date = timezone.now()
            diary.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                diary.file.add(file_instance)
            return redirect('diary:index')
    else:
        form = DiaryForm()
    context = {'form': form}
    return render(request, 'diary/form.html', context)

@login_required(login_url='common:login')
def modify(request, diary_id):
    diary = get_object_or_404(Diary, pk=diary_id)
    if request.user != diary.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('diary:detail', diary_id=diary.id)
    if request.method == "POST":
        form = DiaryForm(request.POST, instance=diary)
        if form.is_valid():
            files = request.FILES.getlist('file')
            delete_file_id_list = request.POST.getlist('delete_attached_file')
            total_files_size = sum([file.size for file in files])
            total_files_size += sum([file.file.size for file in diary.file.all() if str(file.id) not in delete_file_id_list])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'diary/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'diary/form.html', context)
            delete_unused_images(diary.content, request.POST.get('content', ''))
            diary = form.save(commit=False)
            diary.update_date = timezone.now()
            diary.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                diary.file.add(file_instance)
            for file_id in delete_file_id_list:
                file = diary.file.get(pk=file_id)
                diary.file.remove(file.id)
                file_path = file.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            return redirect('diary:detail', diary_id=diary.id)
    else:
        form = DiaryForm(instance=diary)
    context = {'form': form}
    return render(request, 'diary/form.html', context)

@login_required(login_url='common:login')
def delete(request, diary_id):
    diary = get_object_or_404(Diary, pk=diary_id)
    if request.user != diary.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('diary:detail', diary_id=diary.id)
    diary.modify_date = timezone.now()
    diary.use_yn = 'N'
    diary.save()
    return redirect('diary:index')

@login_required(login_url='common:login')
def detail_create(request, diary_id):
    """
    실천내용 등록
    """
    diary = get_object_or_404(Diary, pk=diary_id)
    if request.method == "POST":
        form = DiaryDetailForm(request.POST)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'diary': diary, 'form': form}
                return render(request, 'diary/detail.html', context)
            diarydetail = form.save(commit=False)
            diarydetail.author = request.user
            diarydetail.create_date = timezone.now()
            diarydetail.diary = diary
            diarydetail.save()
            return redirect('{}#diarydetail_{}'.format(resolve_url('diary:detail', diary_id=diary.id), diarydetail.id))
    else:
        form = DiaryDetailForm()
    context = {'diary': diary, 'form': form}
    return render(request, 'diary/detail.html', context)


@login_required(login_url='common:login')
def detail_modify(request, diarydetail_id):
    diarydetail = get_object_or_404(DiaryDetail, pk=diarydetail_id)
    diarydetail_content = diarydetail.content
    if request.user != diarydetail.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('diary:detail', diary_id=diarydetail.diary.id)
    if request.method == "POST":
        form = DiaryDetailForm(request.POST, instance=diarydetail)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'diarydetail':diarydetail, 'form': form}
                return render(request, 'diary/detail_form.html', context)
            delete_unused_images(diarydetail_content, request.POST.get('content', ''))
            diarydetail = form.save(commit=False)
            diarydetail.update_date = timezone.now()
            diarydetail.save()
            return redirect('{}#diarydetail_{}'.format(resolve_url('diary:detail', diary_id=diarydetail.diary.id), diarydetail.id))
    else:
        form = DiaryDetailForm(instance=diarydetail)
    context = {'diarydetail':diarydetail, 'form': form}
    return render(request, 'diary/detail_form.html', context)

@login_required(login_url='common:login')
def detail_delete(request, diarydetail_id):
    diarydetail = get_object_or_404(DiaryDetail, pk=diarydetail_id)
    if request.user != diarydetail.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        diarydetail.update_date = timezone.now()
        diarydetail.use_yn = 'N'
        diarydetail.save()
    return redirect('diary:detail', diary_id=diarydetail.diary.id)

@login_required(login_url='common:login')
def vote(request, diary_id):
    diary = get_object_or_404(Diary, pk=diary_id)
    if request.user == diary.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        diary.voter.add(request.user)
    return redirect('diary:detail', diary_id=diary.id)

@login_required(login_url='common:login')
def detail_vote(request, diarydetail_id):
    diarydetail = get_object_or_404(DiaryDetail, pk=diarydetail_id)
    if request.user == diarydetail.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        diarydetail.voter.add(request.user)
    return redirect('diary:detail', diary_id=diarydetail.diary.id)