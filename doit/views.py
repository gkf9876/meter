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
from .forms import DoitForm, DoitDetailForm
from .models import Doit, DoitDetail


@login_required(login_url='common:login')
def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    doit_list = Doit.objects.filter(Q(author_id=request.user.id) | Q(notice_yn=True), use_yn='Y').order_by('-notice_yn', '-create_date')
    if kw:
        doit_list = doit_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(doitdetail__content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(doitdetail__author__username__icontains=kw)
        ).distinct()
    paginator = Paginator(doit_list, 10)
    page_obj = paginator.get_page(page)
    context = {'doit_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'doit/list.html', context)

@login_required(login_url='common:login')
def detail(request, doit_id):
    doit = get_object_or_404(Doit, Q(author_id=request.user.id) | Q(notice_yn=True), pk=doit_id, use_yn='Y')
    if request.user != doit.author:
        doit.viewcount.add(request.user)
    context = {'doit': doit}
    return render(request, 'doit/detail.html', context)

@login_required(login_url='common:login')
def create(request):
    if request.method == 'POST':
        form = DoitForm(request.POST)
        if form.is_valid():
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'doit/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'doit/form.html', context)
            doit = form.save(commit=False)
            doit.author = request.user
            doit.create_date = timezone.now()
            doit.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                doit.file.add(file_instance)
            return redirect('doit:index')
    else:
        form = DoitForm()
    context = {'form': form}
    return render(request, 'doit/form.html', context)

@login_required(login_url='common:login')
def modify(request, doit_id):
    doit = get_object_or_404(Doit, pk=doit_id)
    if request.user != doit.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('doit:detail', doit_id=doit.id)
    if request.method == "POST":
        form = DoitForm(request.POST, instance=doit)
        if form.is_valid():
            files = request.FILES.getlist('file')
            delete_file_id_list = request.POST.getlist('delete_attached_file')
            total_files_size = sum([file.size for file in files])
            total_files_size += sum([file.file.size for file in doit.file.all() if str(file.id) not in delete_file_id_list])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'doit/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'doit/form.html', context)
            delete_unused_images(doit.content, request.POST.get('content', ''))
            doit = form.save(commit=False)
            doit.update_date = timezone.now()
            doit.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                doit.file.add(file_instance)
            for file_id in delete_file_id_list:
                file = doit.file.get(pk=file_id)
                doit.file.remove(file.id)
                file_path = file.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            return redirect('doit:detail', doit_id=doit.id)
    else:
        form = DoitForm(instance=doit)
    context = {'form': form}
    return render(request, 'doit/form.html', context)

@login_required(login_url='common:login')
def delete(request, doit_id):
    doit = get_object_or_404(Doit, pk=doit_id)
    if request.user != doit.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('doit:detail', doit_id=doit.id)
    doit.modify_date = timezone.now()
    doit.use_yn = 'N'
    doit.save()
    return redirect('doit:index')

@login_required(login_url='common:login')
def detail_create(request, doit_id):
    """
    실천내용 등록
    """
    doit = get_object_or_404(Doit, pk=doit_id)
    if request.method == "POST":
        form = DoitDetailForm(request.POST)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'doit': doit, 'form': form}
                return render(request, 'doit/detail.html', context)
            doitdetail = form.save(commit=False)
            doitdetail.author = request.user
            doitdetail.create_date = timezone.now()
            doitdetail.doit = doit
            doitdetail.save()
            return redirect('{}#doitdetail_{}'.format(resolve_url('doit:detail', doit_id=doit.id), doitdetail.id))
    else:
        form = DoitDetailForm()
    context = {'doit': doit, 'form': form}
    return render(request, 'doit/detail.html', context)


@login_required(login_url='common:login')
def detail_modify(request, doitdetail_id):
    doitdetail = get_object_or_404(DoitDetail, pk=doitdetail_id)
    doitdetail_content = doitdetail.content
    if request.user != doitdetail.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('doit:detail', doit_id=doitdetail.doit.id)
    if request.method == "POST":
        form = DoitDetailForm(request.POST, instance=doitdetail)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'doitdetail':doitdetail, 'form': form}
                return render(request, 'doit/detail_form.html', context)
            delete_unused_images(doitdetail_content, request.POST.get('content', ''))
            doitdetail = form.save(commit=False)
            doitdetail.update_date = timezone.now()
            doitdetail.save()
            return redirect('{}#doitdetail_{}'.format(resolve_url('doit:detail', doit_id=doitdetail.doit.id), doitdetail.id))
    else:
        form = DoitDetailForm(instance=doitdetail)
    context = {'doitdetail':doitdetail, 'form': form}
    return render(request, 'doit/detail_form.html', context)

@login_required(login_url='common:login')
def detail_delete(request, doitdetail_id):
    doitdetail = get_object_or_404(DoitDetail, pk=doitdetail_id)
    if request.user != doitdetail.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        doitdetail.update_date = timezone.now()
        doitdetail.use_yn = 'N'
        doitdetail.save()
    return redirect('doit:detail', doit_id=doitdetail.doit.id)

@login_required(login_url='common:login')
def vote(request, doit_id):
    doit = get_object_or_404(Doit, pk=doit_id)
    if request.user == doit.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        doit.voter.add(request.user)
    return redirect('doit:detail', doit_id=doit.id)

@login_required(login_url='common:login')
def detail_vote(request, doitdetail_id):
    doitdetail = get_object_or_404(DoitDetail, pk=doitdetail_id)
    if request.user == doitdetail.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        doitdetail.voter.add(request.user)
    return redirect('doit:detail', doit_id=doitdetail.doit.id)