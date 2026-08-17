import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone
from datetime import datetime, timedelta

from common.models import File
from common.views import move_temp_images_to_uploads, delete_unused_images
from .forms import ThirdHabitForm, ThirdHabitItemForm, ThirdHabitDetailForm, ThirdHabitItemDetailForm, \
    ThirdHabitItemDetailTimeForm, ThirdHabitItemExpForm
from .models import ThirdHabit, ThirdHabitItem, ThirdHabitDetail, ThirdHabitItemDetail, ThirdHabitItemDetailTime, \
    ThirdHabitItemExp


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
    ThirdHabitItemExpFormSet = modelformset_factory(ThirdHabitItemExp, form=ThirdHabitItemExpForm, extra=0, can_delete=True)
    if request.user != thirdHabit.author:
        thirdHabit.viewcount.add(request.user)
    formset = ThirdHabitFormSet(prefix='item', queryset=thirdHabit.item.filter(use_yn='Y').order_by('create_date'))
    detail_formsets = {}
    detailTime_formsets = {}
    for index, item_form in enumerate(formset):
        item = item_form.instance
        if item.pk:
            detail_queryset = item.detailItem.filter(use_yn='Y').order_by('create_date')
        else:
            detail_queryset = ThirdHabitItemDetail.objects.none()
        ThirdHabitItemDetailFormSet = modelformset_factory(ThirdHabitItemDetail, form=ThirdHabitItemDetailForm, extra=0, can_delete=True)
        detail_formsets[index] = ThirdHabitItemDetailFormSet(
            prefix=f'item-{index}-detail',
            queryset=detail_queryset
        )
        detailTime_formsets[index] = {}
        for detailIndex, detailItem_form in enumerate(detail_formsets[index]):
            detailItem = detailItem_form.instance
            if detailItem.pk:
                detailTime_queryset = detailItem.detailTimeItem.filter(use_yn='Y').order_by('create_date')
            else:
                detailTime_queryset = ThirdHabitItemDetailTime.objects.none()
            ThirdHabitItemDetailTimeFormSet = modelformset_factory(ThirdHabitItemDetailTime, form=ThirdHabitItemDetailTimeForm, extra=0 if detailTime_queryset.exists() else 1, can_delete=True)
            detailTime_formsets[index][detailIndex] = ThirdHabitItemDetailTimeFormSet(
                prefix=f'item-{index}-detail-{detailIndex}-time',
                queryset=detailTime_queryset
            )
    formsetExp = ThirdHabitItemExpFormSet(prefix='itemExp', queryset=thirdHabit.itemExp.filter(use_yn='Y').order_by('create_date'))

    calendar_events = []
    DAY_OFFSET = {
        'SUN': 1,
        'MON': 2,
        'TUE': 3,
        'WED': 4,
        'THU': 5,
        'FRI': 6,
        'SAT': 7,
    }
    for item in thirdHabit.item.filter(use_yn='Y'):
        for detail in item.detailItem.filter(use_yn='Y'):
            for detail_time in detail.detailTimeItem.filter(use_yn='Y'):
                start_date = thirdHabit.start_date + timedelta(
                    days=DAY_OFFSET[detail_time.start_day]
                )
                start_datetime = datetime.combine(
                    start_date,
                    detail_time.start_time
                )
                end_date = thirdHabit.start_date + timedelta(
                    days=DAY_OFFSET[detail_time.end_day]
                )
                end_datetime = datetime.combine(
                    end_date,
                    detail_time.end_time
                )
                calendar_events.append({
                    'id': detail_time.id,
                    'title': detail.content,
                    'start': str(start_datetime),
                    'end': str(end_datetime),
                    'order': 1,
                })
    context = {
        'thirdHabit': thirdHabit
        , 'formset': formset
        , 'detail_formsets': detail_formsets
        , 'detailTime_formsets': detailTime_formsets
        , 'formsetExp': formsetExp
        , 'calendar_events': calendar_events
    }
    return render(request, 'thirdHabit/detail.html', context)

@login_required(login_url='common:login')
def create(request):
    ThirdHabitFormSet = modelformset_factory(ThirdHabitItem, form=ThirdHabitItemForm, extra=0, can_delete=True)
    ThirdHabitItemExpFormSet = modelformset_factory(ThirdHabitItemExp, form=ThirdHabitItemExpForm, extra=0, can_delete=True)
    if request.method == 'POST':
        form = ThirdHabitForm(request.POST)
        formset = ThirdHabitFormSet(request.POST, prefix='item', queryset=ThirdHabitItem.objects.none())
        detail_formsets = {}
        detail_valid = True
        detailTime_formsets = {}
        detailTime_valid = True
        for index, item_form in enumerate(formset):
            ThirdHabitItemDetailFormSet = modelformset_factory(ThirdHabitItemDetail, form=ThirdHabitItemDetailForm, extra=1, can_delete=True)
            detail_formsets[index] = ThirdHabitItemDetailFormSet(
                request.POST,
                prefix=f'item-{index}-detail',
                queryset=ThirdHabitItemDetail.objects.none()
            )
            if not detail_formsets[index].is_valid():
                detail_valid = False
            detailTime_formsets[index] = {}
            for detailIndex, detailItem_form in enumerate(detail_formsets[index]):
                ThirdHabitItemDetailTimeFormSet = modelformset_factory(ThirdHabitItemDetailTime, form=ThirdHabitItemDetailTimeForm, extra=1, can_delete=True)
                detailTime_formsets[index][detailIndex] = ThirdHabitItemDetailTimeFormSet(
                    request.POST,
                    prefix=f'item-{index}-detail-{detailIndex}-time',
                    queryset=ThirdHabitItemDetailTime.objects.none()
                )
                if not detail_formsets[index][detailIndex].is_valid():
                    detailTime_valid = False
        formsetExp = ThirdHabitItemExpFormSet(request.POST, prefix='itemExp', queryset=ThirdHabitItemExp.objects.none())
        if form.is_valid() and formset.is_valid() and detail_valid and detailTime_valid and formsetExp.is_valid():
            files = request.FILES.getlist('file')
            total_files_size = sum([file.size for file in files])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form, 'formset': formset, 'detail_formsets': detail_formsets, 'detailTime_formsets': detailTime_formsets, 'formsetExp': formsetExp}
                return render(request, 'thirdHabit/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form, 'formset': formset, 'detail_formsets': detail_formsets, 'detailTime_formsets': detailTime_formsets, 'formsetExp': formsetExp}
                return render(request, 'thirdHabit/form.html', context)
            thirdHabit = form.save(commit=False)
            thirdHabit.author = request.user
            thirdHabit.create_date = timezone.now()
            thirdHabit.save()
            for index, item_form in enumerate(formset):
                if item_form.instance.pk is None and not item_form.has_changed():
                    continue
                item = item_form.save(commit=False)
                item.update_date = timezone.now()
                item.save()
                thirdHabit.item.add(item)
                for detailIndex, detailItem_form in enumerate(detail_formsets[index]):
                    if detailItem_form.instance.pk is None and not detailItem_form.has_changed():
                        continue
                    detail = detailItem_form.save(commit=False)
                    detail.update_date = timezone.now()
                    detail.save()
                    item.detailItem.add(detail)
                    for detailTimeItemIndex, detailTimeItem_form in enumerate(detailTime_formsets[index][detailIndex]):
                        if detailTimeItem_form.instance.pk is None and not detailTimeItem_form.has_changed():
                            continue
                        detailTimeItem = detailTimeItem_form.save(commit=False)
                        detailTimeItem.update_date = timezone.now()
                        detailTimeItem.save()
                        detail.detailTimeItem.add(detailTimeItem)
            for index, itemExp_form in enumerate(formsetExp):
                if itemExp_form.instance.pk is None and not itemExp_form.has_changed():
                    continue
                item = itemExp_form.save(commit=False)
                item.update_date = timezone.now()
                item.save()
                thirdHabit.itemExp.add(item)
            for file in files:
                file_instance = File()
                file_instance.name = file.name
                file_instance.file = file
                file_instance.save()
                thirdHabit.file.add(file_instance)
            return redirect('thirdHabit:index')
    else:
        form = ThirdHabitForm()
        formset = ThirdHabitFormSet(prefix='item', queryset=ThirdHabitItem.objects.none())
        detail_formsets = {}
        detailTime_formsets = {}
        for index, item_form in enumerate(formset):
            ThirdHabitItemDetailFormSet = modelformset_factory(ThirdHabitItemDetail, form=ThirdHabitItemDetailForm, extra=1, can_delete=True)
            detail_formsets[index] = ThirdHabitItemDetailFormSet(
                prefix=f'item-{index}-detail',
                queryset=ThirdHabitItemDetail.objects.none()
            )
            detailTime_formsets[index] = {}
            for detailIndex, detailItem_form in enumerate(detail_formsets[index]):
                ThirdHabitItemDetailTimeFormSet = modelformset_factory(ThirdHabitItemDetailTime, form=ThirdHabitItemDetailTimeForm, extra=1, can_delete=True)
                detailTime_formsets[index][detailIndex] = ThirdHabitItemDetailTimeFormSet(
                    prefix=f'item-{index}-detail-{detailIndex}-time',
                    queryset=ThirdHabitItemDetailTime.objects.none()
                )
        formsetExp = ThirdHabitItemExpFormSet(prefix='itemExp', queryset=ThirdHabitItemExp.objects.none())
    context = {'form': form, 'formset': formset, 'detail_formsets': detail_formsets, 'detailTime_formsets': detailTime_formsets, 'formsetExp': formsetExp}
    return render(request, 'thirdHabit/form.html', context)

@login_required(login_url='common:login')
def modify(request, thirdHabit_id):
    thirdHabit = get_object_or_404(ThirdHabit, pk=thirdHabit_id)
    thirdHabit_content = thirdHabit.content
    if request.user != thirdHabit.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('thirdHabit:detail', thirdHabit_id=thirdHabit.id)
    if request.method == "POST":
        form = ThirdHabitForm(request.POST, instance=thirdHabit)
        item_queryset = thirdHabit.item.filter(use_yn='Y').order_by('create_date')
        ThirdHabitItemFormSet = modelformset_factory(ThirdHabitItem, form=ThirdHabitItemForm, extra=0 if item_queryset.exists() else 1, can_delete=True)
        formset = ThirdHabitItemFormSet(request.POST, prefix='item', queryset=item_queryset)
        detail_formsets = {}
        detail_valid = True
        detailTime_formsets = {}
        detailTime_valid = True
        for index, item_form in enumerate(formset):
            item = item_form.instance
            if item.pk:
                detail_queryset = item.detailItem.filter(use_yn='Y').order_by('create_date')
            else:
                detail_queryset = ThirdHabitItemDetail.objects.none()
            ThirdHabitItemDetailFormSet = modelformset_factory(ThirdHabitItemDetail, form=ThirdHabitItemDetailForm, extra=0 if detail_queryset.exists() else 1, can_delete=True)
            detail_formsets[index] = ThirdHabitItemDetailFormSet(
                request.POST,
                prefix=f'item-{index}-detail',
                queryset=detail_queryset
            )
            if not detail_formsets[index].is_valid():
                detail_valid = False
            detailTime_formsets[index] = {}
            for detailIndex, detailItem_form in enumerate(detail_formsets[index]):
                detailItem = detailItem_form.instance
                if detailItem.pk:
                    detailTime_queryset = detailItem.detailTimeItem.filter(use_yn='Y').order_by('create_date')
                else:
                    detailTime_queryset = ThirdHabitItemDetailTime.objects.none()
                ThirdHabitItemDetailTimeFormSet = modelformset_factory(ThirdHabitItemDetailTime, form=ThirdHabitItemDetailTimeForm, extra=0 if detailTime_queryset.exists() else 1, can_delete=True)
                detailTime_formsets[index][detailIndex] = ThirdHabitItemDetailTimeFormSet(
                    request.POST,
                    prefix=f'item-{index}-detail-{detailIndex}-time',
                    queryset=detailTime_queryset
                )
                if not detail_formsets[index][detailIndex].is_valid():
                    detailTime_valid = False
        ThirdHabitItemExpFormSet = modelformset_factory(ThirdHabitItemExp, form=ThirdHabitItemExpForm, extra=0, can_delete=True)
        formsetExp = ThirdHabitItemExpFormSet(request.POST, prefix='itemExp', queryset=thirdHabit.itemExp.filter(use_yn='Y').order_by('create_date'))
        if form.is_valid() and formset.is_valid() and detail_valid and detailTime_valid and formsetExp.is_valid():
            files = request.FILES.getlist('file')
            delete_file_id_list = request.POST.getlist('delete_attached_file')
            total_files_size = sum([file.size for file in files])
            total_files_size += sum([file.file.size for file in thirdHabit.file.all() if str(file.id) not in delete_file_id_list])
            if total_files_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.error(request, '첨부파일의 총용량이 %dMB를 초과할 수 없습니다.' % (settings.FILE_UPLOAD_MAX_MEMORY_SIZE/ 1024 / 1024))
                context = {'form': form, 'formset': formset, 'detail_formsets': detail_formsets, 'detailTime_formsets': detailTime_formsets, 'formsetExp': formsetExp}
                return render(request, 'thirdHabit/form.html', context)
            if not move_temp_images_to_uploads(request.POST.get('content', '')):
                messages.error(request, '본문내용의 이미지 첨부 경로에 문제가 있습니다.')
                context = {'form': form, 'formset': formset, 'detail_formsets': detail_formsets, 'detailTime_formsets': detailTime_formsets, 'formsetExp': formsetExp}
                return render(request, 'thirdHabit/form.html', context)
            delete_unused_images(thirdHabit_content, request.POST.get('content', ''))
            thirdHabit = form.save(commit=False)
            thirdHabit.update_date = timezone.now()
            thirdHabit.save()
            for index, item_form in enumerate(formset):
                if item_form.instance.pk is None and not item_form.has_changed():
                    continue
                item = item_form.save(commit=False)
                item.update_date = timezone.now()
                item.save()
                thirdHabit.item.add(item)
                for detailIndex, detailItem_form in enumerate(detail_formsets[index]):
                    if detailItem_form.instance.pk is None and not detailItem_form.has_changed():
                        continue
                    detail = detailItem_form.save(commit=False)
                    detail.update_date = timezone.now()
                    detail.save()
                    item.detailItem.add(detail)
                    for detailTimeItemIndex, detailTimeItem_form in enumerate(detailTime_formsets[index][detailIndex]):
                        if detailTimeItem_form.instance.pk is None and not detailTimeItem_form.has_changed():
                            continue
                        detailTimeItem = detailTimeItem_form.save(commit=False)
                        detailTimeItem.update_date = timezone.now()
                        detailTimeItem.save()
                        detail.detailTimeItem.add(detailTimeItem)
            for index, itemExp_form in enumerate(formsetExp):
                if itemExp_form.instance.pk is None and not itemExp_form.has_changed():
                    continue
                item = itemExp_form.save(commit=False)
                item.update_date = timezone.now()
                item.save()
                thirdHabit.itemExp.add(item)
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
        item_queryset = thirdHabit.item.filter(use_yn='Y').order_by('create_date')
        ThirdHabitItemFormSet = modelformset_factory(ThirdHabitItem, form=ThirdHabitItemForm, extra=0 if item_queryset.exists() else 1, can_delete=True)
        formset = ThirdHabitItemFormSet(prefix='item', queryset=item_queryset)
        detail_formsets = {}
        detailTime_formsets = {}
        for index, item_form in enumerate(formset):
            item = item_form.instance
            if item.pk:
                detail_queryset = item.detailItem.filter(use_yn='Y').order_by('create_date')
            else:
                detail_queryset = ThirdHabitItemDetail.objects.none()
            ThirdHabitItemDetailFormSet = modelformset_factory(ThirdHabitItemDetail, form=ThirdHabitItemDetailForm, extra=0 if detail_queryset.exists() else 1, can_delete=True)
            detail_formsets[index] = ThirdHabitItemDetailFormSet(
                prefix=f'item-{index}-detail',
                queryset=detail_queryset
            )
            detailTime_formsets[index] = {}
            for detailIndex, detailItem_form in enumerate(detail_formsets[index]):
                detailItem = detailItem_form.instance
                if detailItem.pk:
                    detailTime_queryset = detailItem.detailTimeItem.filter(use_yn='Y').order_by('create_date')
                else:
                    detailTime_queryset = ThirdHabitItemDetailTime.objects.none()
                ThirdHabitItemDetailTimeFormSet = modelformset_factory(ThirdHabitItemDetailTime, form=ThirdHabitItemDetailTimeForm, extra=0 if detailTime_queryset.exists() else 1, can_delete=True)
                detailTime_formsets[index][detailIndex] = ThirdHabitItemDetailTimeFormSet(
                    prefix=f'item-{index}-detail-{detailIndex}-time',
                    queryset=detailTime_queryset
                )
        ThirdHabitItemExpFormSet = modelformset_factory(ThirdHabitItemExp, form=ThirdHabitItemExpForm, extra=0, can_delete=True)
        formsetExp = ThirdHabitItemExpFormSet(prefix='itemExp', queryset=thirdHabit.itemExp.filter(use_yn='Y').order_by('create_date'))
    context = {'form': form, 'formset': formset, 'detail_formsets': detail_formsets, 'detailTime_formsets': detailTime_formsets, 'formsetExp': formsetExp}
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