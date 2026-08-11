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
from common.views import move_temp_images_to_uploads, delete_unused_images
from .forms import ThirdHabitForm, ThirdHabitItemForm, ThirdHabitDetailForm, ThirdHabitItemDetailForm
from .models import ThirdHabit, ThirdHabitItem, ThirdHabitDetail, ThirdHabitItemDetail


@login_required(login_url='common:login')
def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    thirdHabit_list = ThirdHabit.objects.filter(Q(author_id=request.user.id) | Q(notice_yn=True), use_yn='Y').order_by('-notice_yn', '-create_date')
    if kw:
        thirdHabit_list = thirdHabit_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(thirdHabitItem__content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(thirdHabitItem__author__username__icontains=kw)
        ).distinct()
    paginator = Paginator(thirdHabit_list, 10)
    page_obj = paginator.get_page(page)
    context = {'thirdHabit_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'thirdHabit/list.html', context)

@login_required(login_url='common:login')
def detail(request, thirdHabit_id):
    thirdHabit = get_object_or_404(ThirdHabit, Q(author_id=request.user.id) | Q(notice_yn=True), pk=thirdHabit_id, use_yn='Y')
    ThirdHabitFormSet = modelformset_factory(ThirdHabitItem, form=ThirdHabitItemForm, extra=0, can_delete=True)
    if request.user != thirdHabit.author:
        thirdHabit.viewcount.add(request.user)
    formset = ThirdHabitFormSet(queryset=thirdHabit.item.filter(use_yn='Y').order_by('create_date'))
    context = {'thirdHabit': thirdHabit, 'formset': formset}
    return render(request, 'thirdHabit/detail.html', context)

@login_required(login_url='common:login')
def create(request):
    ThirdHabitFormSet = modelformset_factory(ThirdHabitItem, form=ThirdHabitItemForm, extra=0, can_delete=True)

    if request.method == 'POST':
        form = ThirdHabitForm(request.POST)
        formset = ThirdHabitFormSet(request.POST, queryset=ThirdHabitItem.objects.none())
        if form.is_valid() and formset.is_valid():
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form, 'formset': formset}
                return render(request, 'thirdHabit/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form, 'formset': formset}
                return render(request, 'thirdHabit/form.html', context)
            thirdHabit = form.save(commit=False)
            thirdHabit.author = request.user
            thirdHabit.create_date = timezone.now()
            thirdHabit.save()
            thirdHabit_items = formset.save(commit=False)
            for item in thirdHabit_items:
                item.save()
                thirdHabit.item.add(item)
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                thirdHabit.file.add(file_instance)
            return redirect('thirdHabit:index')
    else:
        form = ThirdHabitForm()
        formset = ThirdHabitFormSet(queryset=ThirdHabitItem.objects.none())
    context = {'form': form, 'formset': formset}
    return render(request, 'thirdHabit/form.html', context)

@login_required(login_url='common:login')
def modify(request, thirdHabit_id):
    thirdHabit = get_object_or_404(ThirdHabit, pk=thirdHabit_id)
    ThirdHabitItemFormSet = modelformset_factory(ThirdHabitItem, form=ThirdHabitItemForm, extra=0, can_delete=True)
    ThirdHabitItemDetailFormSet = modelformset_factory(ThirdHabitItemDetail, form=ThirdHabitItemDetailForm, extra=0, can_delete=True)
    thirdHabit_content = thirdHabit.content
    if request.user != thirdHabit.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('thirdHabit:detail', thirdHabit_id=thirdHabit.id)
    if request.method == "POST":
        form = ThirdHabitForm(request.POST, instance=thirdHabit)
        formset = ThirdHabitItemFormSet(request.POST, prefix='item', queryset=thirdHabit.item.filter(use_yn='Y').order_by('create_date'))
        detail_formsets = {}
        detail_valid = True
        for index, item_form in enumerate(formset):
            item = item_form.instance

            if item.pk:
                detail_queryset = item.detailItem.filter(use_yn='Y').order_by('create_date')
            else:
                detail_queryset = ThirdHabitItemDetail.objects.none()

            detail_formsets[index] = ThirdHabitItemDetailFormSet(
                request.POST,
                prefix=f'item-{index}-detail',
                queryset=detail_queryset
            )
            if not detail_formsets[index].is_valid():
                detail_valid = False
                break
        if form.is_valid() and formset.is_valid() and detail_valid:
            files = request.FILES.getlist('file')
            delete_file_id_list = request.POST.getlist('delete_attached_file')
            total_files_size = sum([file.size for file in files])
            total_files_size += sum([file.file.size for file in thirdHabit.file.all() if str(file.id) not in delete_file_id_list])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form, 'formset': formset}
                return render(request, 'thirdHabit/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form, 'formset': formset}
                return render(request, 'thirdHabit/form.html', context)
            delete_unused_images(thirdHabit_content, request.POST.get('content', ''))
            thirdHabit = form.save(commit=False)
            thirdHabit.update_date = timezone.now()
            thirdHabit.save()

            for index, item_form in enumerate(formset):
                item = item_form.instance
                item.update_date = timezone.now()
                item.save()
                thirdHabit.item.add(item)
                thirdHabit_detailItems = detail_formsets[index].save(commit=False)
                for detail in thirdHabit_detailItems:
                    detail.save()
                    item.detailItem.add(detail)
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                thirdHabit.file.add(file_instance)
            for file_id in delete_file_id_list:
                file = thirdHabit.file.get(pk=file_id)
                thirdHabit.file.remove(file.id)
                file_path = file.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            return redirect('thirdHabit:detail', thirdHabit_id=thirdHabit.id)
    else:
        form = ThirdHabitForm(instance=thirdHabit)
        formset = ThirdHabitItemFormSet(prefix='item', queryset=thirdHabit.item.filter(use_yn='Y').order_by('create_date'))
        detail_formsets = {}
        for index, item_form in enumerate(formset):
            item = item_form.instance
            detail_formsets[item.id] = ThirdHabitItemDetailFormSet(
                prefix=f'item-{index}-detail',
                queryset=item.detailItem.filter(use_yn='Y').order_by('create_date')
            )
    context = {'form': form, 'formset': formset, 'detail_formsets': detail_formsets}
    return render(request, 'thirdHabit/form.html', context)

@login_required(login_url='common:login')
def delete(request, thirdHabit_id):
    thirdHabit = get_object_or_404(ThirdHabit, pk=thirdHabit_id)
    if request.user != thirdHabit.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('thirdHabit:detail', thirdHabit_id=thirdHabit.id)
    thirdHabit.modify_date = timezone.now()
    thirdHabit.use_yn = 'N'
    thirdHabit.save()
    return redirect('thirdHabit:index')

@login_required(login_url='common:login')
def detail_create(request, thirdHabit_id):
    """
    실천내용 등록
    """
    thirdHabit = get_object_or_404(ThirdHabit, pk=thirdHabit_id)
    if request.method == "POST":
        form = ThirdHabitDetailForm(request.POST)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'thirdHabit': thirdHabit, 'form': form}
                return render(request, 'thirdHabit/detail.html', context)
            thirdHabitDetail = form.save(commit=False)
            thirdHabitDetail.author = request.user
            thirdHabitDetail.create_date = timezone.now()
            thirdHabitDetail.thirdHabit = thirdHabit
            thirdHabitDetail.save()
            return redirect('{}#thirdHabitDetail_{}'.format(resolve_url('thirdHabit:detail', thirdHabit_id=thirdHabit.id), thirdHabitDetail.id))
    else:
        form = ThirdHabitDetailForm()
    context = {'thirdHabit': thirdHabit, 'form': form}
    return render(request, 'thirdHabit/detail.html', context)


@login_required(login_url='common:login')
def detail_modify(request, thirdHabitDetail_id):
    thirdHabitDetail = get_object_or_404(ThirdHabitDetail, pk=thirdHabitDetail_id)
    thirdHabitDetail_content = thirdHabitDetail.content
    if request.user != thirdHabitDetail.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('thirdHabit:detail', thirdHabit_id=thirdHabitDetail.thirdHabit.id)
    if request.method == "POST":
        form = ThirdHabitDetailForm(request.POST, instance=thirdHabitDetail)
        if form.is_valid():
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'thirdHabitDetail':thirdHabitDetail, 'form': form}
                return render(request, 'thirdHabit/detail_form.html', context)
            delete_unused_images(thirdHabitDetail_content, request.POST.get('content', ''))
            thirdHabitDetail = form.save(commit=False)
            thirdHabitDetail.update_date = timezone.now()
            thirdHabitDetail.save()
            return redirect('{}#thirdHabitDetail_{}'.format(resolve_url('thirdHabit:detail', thirdHabit_id=thirdHabitDetail.thirdHabit.id), thirdHabitDetail.id))
    else:
        form = ThirdHabitDetailForm(instance=thirdHabitDetail)
    context = {'thirdHabitDetail':thirdHabitDetail, 'form': form}
    return render(request, 'thirdHabit/detail_form.html', context)

@login_required(login_url='common:login')
def detail_delete(request, thirdHabitDetail_id):
    thirdHabitDetail = get_object_or_404(ThirdHabitDetail, pk=thirdHabitDetail_id)
    if request.user != thirdHabitDetail.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        thirdHabitDetail.update_date = timezone.now()
        thirdHabitDetail.use_yn = 'N'
        thirdHabitDetail.save()
    return redirect('thirdHabit:detail', thirdHabit_id=thirdHabitDetail.thirdHabit.id)

@login_required(login_url='common:login')
def vote(request, thirdHabit_id):
    thirdHabit = get_object_or_404(ThirdHabit, pk=thirdHabit_id)
    if request.user == thirdHabit.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        thirdHabit.voter.add(request.user)
    return redirect('thirdHabit:detail', thirdHabit_id=thirdHabit.id)

@login_required(login_url='common:login')
def detail_vote(request, thirdHabitDetail_id):
    thirdHabitDetail = get_object_or_404(ThirdHabitDetail, pk=thirdHabitDetail_id)
    if request.user == thirdHabitDetail.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        thirdHabitDetail.voter.add(request.user)
    return redirect('thirdHabit:detail', thirdHabit_id=thirdHabitDetail.thirdHabit.id)