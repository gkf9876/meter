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
from .forms import CommunityForm, CommunityDetailForm
from .models import Community, CommunityDetail


@login_required(login_url='common:login')
def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    community_list = Community.objects.filter(Q(author_id=request.user.id) | Q(notice_yn=True), use_yn='Y').order_by('-notice_yn', '-create_date')
    if kw:
        community_list = community_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(communitydetail__content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(communitydetail__author__username__icontains=kw)
        ).distinct()
    paginator = Paginator(community_list, 10)
    page_obj = paginator.get_page(page)
    context = {'community_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'community/list.html', context)

@login_required(login_url='common:login')
def detail(request, community_id):
    community = get_object_or_404(Community, Q(author_id=request.user.id) | Q(notice_yn=True), pk=community_id, use_yn='Y')
    if request.user != community.author:
        community.viewcount.add(request.user)
    context = {'community': community}
    return render(request, 'community/detail.html', context)

@login_required(login_url='common:login')
def create(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'community/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'community/form.html', context)
            community = form.save(commit=False)
            community.author = request.user
            community.create_date = timezone.now()
            community.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                community.file.add(file_instance)
            return redirect('community:index')
    else:
        form = CommunityForm()
    context = {'form': form}
    return render(request, 'community/form.html', context)

@login_required(login_url='common:login')
def modify(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    if request.user != community.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('community:detail', community_id=community.id)
    if request.method == "POST":
        form = CommunityForm(request.POST, instance=community)
        if form.is_valid():
            files = request.FILES.getlist('file')
            delete_file_id_list = request.POST.getlist('delete_attached_file')
            total_files_size = sum([file.size for file in files])
            total_files_size += sum([file.file.size for file in community.file.all() if str(file.id) not in delete_file_id_list])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'community/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'community/form.html', context)
            delete_unused_images(community.content, request.POST.get('content', ''))
            community = form.save(commit=False)
            community.update_date = timezone.now()
            community.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                community.file.add(file_instance)
            for file_id in delete_file_id_list:
                file = community.file.get(pk=file_id)
                community.file.remove(file.id)
                file_path = file.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            return redirect('community:detail', community_id=community.id)
    else:
        form = CommunityForm(instance=community)
    context = {'form': form}
    return render(request, 'community/form.html', context)

@login_required(login_url='common:login')
def delete(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    if request.user != community.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('community:detail', community_id=community.id)
    community.modify_date = timezone.now()
    community.use_yn = 'N'
    community.save()
    return redirect('community:index')

@login_required(login_url='common:login')
def detail_create(request, community_id):
    """
    실천내용 등록
    """
    community = get_object_or_404(Community, pk=community_id)
    if request.method == "POST":
        form = CommunityDetailForm(request.POST)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'community': community, 'form': form}
                return render(request, 'community/detail.html', context)
            communitydetail = form.save(commit=False)
            communitydetail.author = request.user
            communitydetail.create_date = timezone.now()
            communitydetail.community = community
            communitydetail.save()
            return redirect('{}#communitydetail_{}'.format(resolve_url('community:detail', community_id=community.id), communitydetail.id))
    else:
        form = CommunityDetailForm()
    context = {'community': community, 'form': form}
    return render(request, 'community/detail.html', context)


@login_required(login_url='common:login')
def detail_modify(request, communitydetail_id):
    communitydetail = get_object_or_404(CommunityDetail, pk=communitydetail_id)
    communitydetail_content = communitydetail.content
    if request.user != communitydetail.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('community:detail', community_id=communitydetail.community.id)
    if request.method == "POST":
        form = CommunityDetailForm(request.POST, instance=communitydetail)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'communitydetail':communitydetail, 'form': form}
                return render(request, 'community/detail_form.html', context)
            delete_unused_images(communitydetail_content, request.POST.get('content', ''))
            communitydetail = form.save(commit=False)
            communitydetail.update_date = timezone.now()
            communitydetail.save()
            return redirect('{}#communitydetail_{}'.format(resolve_url('community:detail', community_id=communitydetail.community.id), communitydetail.id))
    else:
        form = CommunityDetailForm(instance=communitydetail)
    context = {'communitydetail':communitydetail, 'form': form}
    return render(request, 'community/detail_form.html', context)

@login_required(login_url='common:login')
def detail_delete(request, communitydetail_id):
    communitydetail = get_object_or_404(CommunityDetail, pk=communitydetail_id)
    if request.user != communitydetail.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        communitydetail.update_date = timezone.now()
        communitydetail.use_yn = 'N'
        communitydetail.save()
    return redirect('community:detail', community_id=communitydetail.community.id)

@login_required(login_url='common:login')
def vote(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    if request.user == community.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        community.voter.add(request.user)
    return redirect('community:detail', community_id=community.id)

@login_required(login_url='common:login')
def detail_vote(request, communitydetail_id):
    communitydetail = get_object_or_404(CommunityDetail, pk=communitydetail_id)
    if request.user == communitydetail.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        communitydetail.voter.add(request.user)
    return redirect('community:detail', community_id=communitydetail.community.id)