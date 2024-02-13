from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import MemorizationForm
from .models import Memorization


@login_required(login_url='common:login')
def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    memorization_list = Memorization.objects.filter(author_id=request.user.id, use_yn='Y').order_by('-create_date')
    if kw:
        memorization_list = memorization_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(author__username__icontains=kw)
        ).distinct()
    paginator = Paginator(memorization_list, 10)
    page_obj = paginator.get_page(page)
    context = {'memorization_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'memorization/list.html', context)

@login_required(login_url='common:login')
def detail(request, memorization_id):
    memorization = get_object_or_404(Memorization, pk=memorization_id, author_id=request.user.id, use_yn='Y')
    context = {'memorization': memorization}
    return render(request, 'memorization/detail.html', context)


@login_required(login_url='common:login')
def create(request):
    if request.method == 'POST':
        memorization_form = MemorizationForm(request.POST)
        if memorization_form.is_valid():
            memorization = memorization_form.save(commit=False)
            memorization.author = request.user
            memorization.create_date = timezone.now()
            memorization.save()
            return redirect('memorization:index')
    else:
        form = MemorizationForm()
    context = {'form': form}
    return render(request, 'memorization/form.html', context)

@login_required(login_url='common:login')
def modify(request, memorization_id):
    memorization = get_object_or_404(Memorization, pk=memorization_id, author_id=request.user.id, use_yn='Y')
    if request.user != memorization.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('memorization:detail', memorization_id=memorization.id)
    if request.method == "POST":
        form = MemorizationForm(request.POST, instance=memorization)
        if form.is_valid():
            memorization = form.save(commit=False)
            memorization.modify_date = timezone.now()
            memorization.save()
            return redirect('memorization:detail', memorization_id=memorization.id)
    else:
        form = MemorizationForm(instance=memorization)
    context = {'form': form}
    return render(request, 'memorization/form.html', context)

@login_required(login_url='common:login')
def delete(request, memorization_id):
    memorization = get_object_or_404(Memorization, pk=memorization_id, author_id=request.user.id, use_yn='Y')
    if request.user != memorization.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('memorization:detail', memorization_id=memorization.id)
    memorization.modify_date = timezone.now()
    memorization.use_yn = "N"
    memorization.save()
    return redirect('memorization:index')