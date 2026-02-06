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
from .forms import RelationshipForm, RelationshipDetailForm
from .models import Relationship, RelationshipDetail


@login_required(login_url='common:login')
@permission_required('relationship.view_relationship', raise_exception=False)
def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    relationship_list = Relationship.objects.filter(Q(author_id=request.user.id) | Q(notice_yn=True), use_yn='Y').order_by('-notice_yn', '-create_date')
    if kw:
        relationship_list = relationship_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(relationshipdetail__content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(relationshipdetail__author__username__icontains=kw)
        ).distinct()
    paginator = Paginator(relationship_list, 10)
    page_obj = paginator.get_page(page)
    context = {'relationship_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'relationship/list.html', context)

@login_required(login_url='common:login')
@permission_required('relationship.view_relationship', raise_exception=False)
def detail(request, relationship_id):
    relationship = get_object_or_404(Relationship, Q(author_id=request.user.id) | Q(notice_yn=True), pk=relationship_id, use_yn='Y')
    if request.user != relationship.author:
        relationship.viewcount.add(request.user)
    context = {'relationship': relationship}
    return render(request, 'relationship/detail.html', context)

@login_required(login_url='common:login')
@permission_required('relationship.add_relationship', raise_exception=False)
def create(request):
    if request.method == 'POST':
        form = RelationshipForm(request.POST)
        if form.is_valid():
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'relationship/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'relationship/form.html', context)
            relationship = form.save(commit=False)
            relationship.author = request.user
            relationship.create_date = timezone.now()
            relationship.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                relationship.file.add(file_instance)
            return redirect('relationship:index')
    else:
        form = RelationshipForm()
    context = {'form': form}
    return render(request, 'relationship/form.html', context)

@login_required(login_url='common:login')
@permission_required('relationship.change_relationship', raise_exception=False)
def modify(request, relationship_id):
    relationship = get_object_or_404(Relationship, pk=relationship_id)
    if request.user != relationship.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('relationship:detail', relationship_id=relationship.id)
    if request.method == "POST":
        form = RelationshipForm(request.POST, instance=relationship)
        if form.is_valid():
            files = request.FILES.getlist('file')
            delete_file_id_list = request.POST.getlist('delete_attached_file')
            total_files_size = sum([file.size for file in files])
            total_files_size += sum([file.file.size for file in relationship.file.all() if str(file.id) not in delete_file_id_list])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form}
                return render(request, 'relationship/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form}
                return render(request, 'relationship/form.html', context)
            delete_unused_images(relationship.content, request.POST.get('content', ''))
            relationship = form.save(commit=False)
            relationship.update_date = timezone.now()
            relationship.save()
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                relationship.file.add(file_instance)
            for file_id in delete_file_id_list:
                file = relationship.file.get(pk=file_id)
                relationship.file.remove(file.id)
                file_path = file.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            return redirect('relationship:detail', relationship_id=relationship.id)
    else:
        form = RelationshipForm(instance=relationship)
    context = {'form': form}
    return render(request, 'relationship/form.html', context)

@login_required(login_url='common:login')
@permission_required('relationship.delete_relationship', raise_exception=False)
def delete(request, relationship_id):
    relationship = get_object_or_404(Relationship, pk=relationship_id)
    if request.user != relationship.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('relationship:detail', relationship_id=relationship.id)
    relationship.modify_date = timezone.now()
    relationship.use_yn = 'N'
    relationship.save()
    return redirect('relationship:index')

@login_required(login_url='common:login')
@permission_required('relationship.add_relationshipdetail', raise_exception=False)
def detail_create(request, relationship_id):
    """
    실천내용 등록
    """
    relationship = get_object_or_404(Relationship, pk=relationship_id)
    if request.method == "POST":
        form = RelationshipDetailForm(request.POST)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'relationship': relationship, 'form': form}
                return render(request, 'relationship/detail.html', context)
            relationshipdetail = form.save(commit=False)
            relationshipdetail.author = request.user
            relationshipdetail.create_date = timezone.now()
            relationshipdetail.relationship = relationship
            relationshipdetail.save()
            return redirect('{}#relationshipdetail_{}'.format(resolve_url('relationship:detail', relationship_id=relationship.id), relationshipdetail.id))
    else:
        form = RelationshipDetailForm()
    context = {'relationship': relationship, 'form': form}
    return render(request, 'relationship/detail.html', context)


@login_required(login_url='common:login')
@permission_required('relationship.change_relationshipdetail', raise_exception=False)
def detail_modify(request, relationshipdetail_id):
    relationshipdetail = get_object_or_404(RelationshipDetail, pk=relationshipdetail_id)
    relationshipdetail_content = relationshipdetail.content
    if request.user != relationshipdetail.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('relationship:detail', relationship_id=relationshipdetail.relationship.id)
    if request.method == "POST":
        form = RelationshipDetailForm(request.POST, instance=relationshipdetail)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'relationshipdetail':relationshipdetail, 'form': form}
                return render(request, 'relationship/detail_form.html', context)
            delete_unused_images(relationshipdetail_content, request.POST.get('content', ''))
            relationshipdetail = form.save(commit=False)
            relationshipdetail.update_date = timezone.now()
            relationshipdetail.save()
            return redirect('{}#relationshipdetail_{}'.format(resolve_url('relationship:detail', relationship_id=relationshipdetail.relationship.id), relationshipdetail.id))
    else:
        form = RelationshipDetailForm(instance=relationshipdetail)
    context = {'relationshipdetail':relationshipdetail, 'form': form}
    return render(request, 'relationship/detail_form.html', context)

@login_required(login_url='common:login')
@permission_required('relationship.delete_relationshipdetail', raise_exception=False)
def detail_delete(request, relationshipdetail_id):
    relationshipdetail = get_object_or_404(RelationshipDetail, pk=relationshipdetail_id)
    if request.user != relationshipdetail.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        relationshipdetail.update_date = timezone.now()
        relationshipdetail.use_yn = 'N'
        relationshipdetail.save()
    return redirect('relationship:detail', relationship_id=relationshipdetail.relationship.id)

@login_required(login_url='common:login')
@permission_required('relationship.view_relationship', raise_exception=False)
def vote(request, relationship_id):
    relationship = get_object_or_404(Relationship, pk=relationship_id)
    if request.user == relationship.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        relationship.voter.add(request.user)
    return redirect('relationship:detail', relationship_id=relationship.id)

@login_required(login_url='common:login')
@permission_required('relationship.view_relationshipdetail', raise_exception=False)
def detail_vote(request, relationshipdetail_id):
    relationshipdetail = get_object_or_404(RelationshipDetail, pk=relationshipdetail_id)
    if request.user == relationshipdetail.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        relationshipdetail.voter.add(request.user)
    return redirect('relationship:detail', relationship_id=relationshipdetail.relationship.id)